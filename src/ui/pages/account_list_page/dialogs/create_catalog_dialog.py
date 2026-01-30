import flet as ft
import sqlite3
import re
from src.utils.paths import get_db_path
from data.catalogoOps import crear_tipo_cuenta, crear_rubro, crear_generico
from data.obtenerCuentas import (
    obtenerTodasTipoCuentas,
    obtenerTodosRubroPorTipoCuenta,
    obtenerTipoCuentasPorPlanCuenta,
)


def _snack(page: ft.Page, msg: str, ok: bool):
    page.snack_bar = ft.SnackBar(content=ft.Text(msg), bgcolor=ft.Colors.GREEN if ok else ft.Colors.RED)
    page.snack_bar.open = True
    page.update()


def open_create_tipo_dialog(page: ft.Page, refresh_callback=None, plan_id: int | None = 0):
    db_path = get_db_path()
    nombre_field = ft.TextField(label="Nombre del tipo", width=380, border_color=ft.Colors.BLUE, color=ft.Colors.BLACK)
    codigo_preview = ft.Text("Código sugerido: -", color=ft.Colors.GREY_700)

    # Calcular código sugerido: siguiente número dentro del plan con formato N.0.0.000
    sugerido = "1.0.0.000"
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            if plan_id is None:
                cur.execute("SELECT numero_cuenta FROM tipo_cuenta")
            else:
                cur.execute("SELECT numero_cuenta FROM tipo_cuenta WHERE id_plan_cuenta = ?", (int(plan_id or 0),))
            max_tipo = 0
            for (nc,) in cur.fetchall():
                # Aceptar formatos previos, extraer primer número
                m = re.match(r"^(\d+)", str(nc) or "")
                if m:
                    try:
                        max_tipo = max(max_tipo, int(m.group(1)))
                    except Exception:
                        pass
            nxt = max_tipo + 1
            sugerido = f"{nxt}.0.0.000"
    except Exception as ex:
        print(f"Error calculando sugerido tipo: {ex}")
    codigo_preview.value = f"Código sugerido: {sugerido}"

    def close(dlg):
        dlg.open = False
        page.update()

    def submit(_):
        ok, msg, _new_id = crear_tipo_cuenta(db_path, nombre_field.value or "", sugerido, int(plan_id or 0))
        close(dlg)
        _snack(page, msg, ok)
        if ok and refresh_callback:
            try:
                refresh_callback()
            except Exception as ex:
                print(f"Refresh error tras crear tipo: {ex}")

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Nuevo Tipo de Cuenta", color=ft.Colors.BLUE),
        content=ft.Container(
            content=ft.Column([codigo_preview, nombre_field], spacing=10),
            width=520,
            bgcolor=ft.Colors.WHITE,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: close(dlg), style=ft.ButtonStyle(color=ft.Colors.BLUE)),
            ft.ElevatedButton("Crear", icon=ft.Icons.SAVE, on_click=submit, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=ft.Colors.WHITE,
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()


def open_create_rubro_dialog(page: ft.Page, refresh_callback=None, plan_id: int | None = None):
    db_path = get_db_path()
    if plan_id is None:
        tipos = obtenerTodasTipoCuentas(db_path)
    else:
        tipos = obtenerTipoCuentasPorPlanCuenta(db_path, int(plan_id))

    tipo_label = ft.Text("Seleccione tipo de cuenta", color=ft.Colors.GREY)
    tipo_menu = ft.PopupMenuButton(content=ft.Container(content=ft.Row([tipo_label, ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=ft.Colors.GREY)]), padding=10, border=ft.border.all(1, ft.Colors.GREY_400), border_radius=5, bgcolor=ft.Colors.WHITE), items=[], disabled=True)
    nombre_field = ft.TextField(label="Nombre del rubro", width=380, border_color=ft.Colors.BLUE, color=ft.Colors.BLACK)
    codigo_preview = ft.Text("Código sugerido: -", color=ft.Colors.GREY_700)

    selected_tipo = {"id": None, "nombre": None, "numero": None}

    def close(dlg):
        dlg.open = False
        page.update()

    def select_tipo(data):
        selected_tipo.update(data)
        tipo_label.value = f"{data['numero']} - {data['nombre']}"
        tipo_label.color = ft.Colors.BLACK
        tipo_menu.content.border = ft.border.all(1, ft.Colors.BLUE)
        page.update()

        # Calcular sugerido para rubro como {tipo}.{n}.0.000
        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT numero_cuenta FROM rubro WHERE id_tipo_cuenta = ?", (int(data["id"]),))
                max_suffix = 0
                base_tipo = 0
                mt = re.match(r"^(\d+)", str(data["numero"]) or "")
                if mt:
                    base_tipo = int(mt.group(1))
                for (nc,) in cur.fetchall():
                    # Aceptar formatos previos y nuevos
                    m = re.match(r"^(\d+)\.(\d+)", str(nc) or "")
                    if m and int(m.group(1)) == base_tipo:
                        try:
                            max_suffix = max(max_suffix, int(m.group(2)))
                        except Exception:
                            pass
                codigo_preview.value = f"Código sugerido: {base_tipo}.{max_suffix+1}.0.000"
                page.update()
        except Exception as ex:
            print(f"Error sugiriendo código rubro: {ex}")

    tipo_menu.items = [
        ft.PopupMenuItem(
            content=ft.Row([ft.Text(t.numero_cuenta, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK), ft.Text(t.nombre_tipo_cuenta, color=ft.Colors.BLACK)], spacing=8),
            data={"id": t.id_tipo_cuenta, "nombre": t.nombre_tipo_cuenta, "numero": t.numero_cuenta},
            on_click=lambda e: select_tipo(e.control.data),
        ) for t in tipos
    ]
    tipo_menu.disabled = False

    def submit(_):
        if not selected_tipo["id"]:
            _snack(page, "Debe seleccionar un tipo", False)
            return
        # Usar el valor de preview sin el prefijo
        sugerido = codigo_preview.value.replace("Código sugerido: ", "")
        ok, msg, _new_id = crear_rubro(db_path, int(selected_tipo["id"]), nombre_field.value or "", sugerido)
        close(dlg)
        _snack(page, msg, ok)
        if ok and refresh_callback:
            try:
                refresh_callback()
            except Exception as ex:
                print(f"Refresh error tras crear rubro: {ex}")

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Nuevo Rubro", color=ft.Colors.BLUE),
        content=ft.Container(
            content=ft.Column([
                tipo_menu,
                codigo_preview,
                nombre_field,
            ], spacing=10),
            width=520,
            bgcolor=ft.Colors.WHITE,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: close(dlg), style=ft.ButtonStyle(color=ft.Colors.BLUE)),
            ft.ElevatedButton("Crear", icon=ft.Icons.SAVE, on_click=submit, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=ft.Colors.WHITE,
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()


def open_create_generico_dialog(page: ft.Page, refresh_callback=None, plan_id: int | None = None):
    db_path = get_db_path()
    if plan_id is None:
        tipos = obtenerTodasTipoCuentas(db_path)
    else:
        tipos = obtenerTipoCuentasPorPlanCuenta(db_path, int(plan_id))

    tipo_label = ft.Text("Seleccione tipo", color=ft.Colors.GREY)
    tipo_menu = ft.PopupMenuButton(content=ft.Container(content=ft.Row([tipo_label, ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=ft.Colors.GREY)]), padding=10, border=ft.border.all(1, ft.Colors.GREY_400), border_radius=5, bgcolor=ft.Colors.WHITE), items=[], disabled=True)
    rubro_label = ft.Text("Seleccione rubro", color=ft.Colors.GREY)
    rubro_menu = ft.PopupMenuButton(content=ft.Container(content=ft.Row([rubro_label, ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=ft.Colors.GREY)]), padding=10, border=ft.border.all(1, ft.Colors.GREY_400), border_radius=5, bgcolor=ft.Colors.WHITE), items=[], disabled=True)

    nombre_field = ft.TextField(label="Nombre del genérico", width=380, border_color=ft.Colors.BLUE, color=ft.Colors.BLACK)
    codigo_preview = ft.Text("Código sugerido: -", color=ft.Colors.GREY_700)

    selected_tipo = {"id": None}
    selected_rubro = {"id": None}

    def close(dlg):
        dlg.open = False
        page.update()

    def select_tipo(data):
        selected_tipo["id"] = data["id"]
        tipo_label.value = f"{data['numero']} - {data['nombre']}"
        tipo_label.color = ft.Colors.BLACK
        tipo_menu.content.border = ft.border.all(1, ft.Colors.BLUE)
        # cargar rubros
        rubros = obtenerTodosRubroPorTipoCuenta(db_path, int(data["id"]))
        rubro_menu.items = [
            ft.PopupMenuItem(
                content=ft.Row([ft.Text(r.numero_cuenta, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK), ft.Text(r.nombre_rubro, color=ft.Colors.BLACK)], spacing=8),
                data={"id": r.id_rubro, "nombre": r.nombre_rubro, "numero": r.numero_cuenta},
                on_click=lambda e: select_rubro(e.control.data),
            ) for r in rubros
        ]
        rubro_menu.disabled = False
        page.update()

    def select_rubro(data):
        selected_rubro["id"] = data["id"]
        rubro_label.value = f"{data['numero']} - {data['nombre']}"
        rubro_label.color = ft.Colors.BLACK
        rubro_menu.content.border = ft.border.all(1, ft.Colors.BLUE)
        page.update()

        # Calcular sugerido para genérico como {tipo}.{rubroSeq}.{n}.000
        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT numero_cuenta FROM generico WHERE id_rubro = ?", (int(data["id"]),))
                max_suffix = 0
                base_tipo = 0
                base_rubro = 0
                mr = re.match(r"^(\d+)\.(\d+)", str(data["numero"]) or "")
                if mr:
                    base_tipo = int(mr.group(1))
                    base_rubro = int(mr.group(2))
                for (nc,) in cur.fetchall():
                    m = re.match(r"^(\d+)\.(\d+)\.(\d+)", str(nc) or "")
                    if m and int(m.group(1)) == base_tipo and int(m.group(2)) == base_rubro:
                        try:
                            max_suffix = max(max_suffix, int(m.group(3)))
                        except Exception:
                            pass
                codigo_preview.value = f"Código sugerido: {base_tipo}.{base_rubro}.{max_suffix+1}.000"
                page.update()
        except Exception as ex:
            print(f"Error sugiriendo código genérico: {ex}")

    tipo_menu.items = [
        ft.PopupMenuItem(
            content=ft.Row([ft.Text(t.numero_cuenta, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK), ft.Text(t.nombre_tipo_cuenta, color=ft.Colors.BLACK)], spacing=8),
            data={"id": t.id_tipo_cuenta, "nombre": t.nombre_tipo_cuenta, "numero": t.numero_cuenta},
            on_click=lambda e: select_tipo(e.control.data),
        ) for t in tipos
    ]
    tipo_menu.disabled = False

    def submit(_):
        if not selected_rubro["id"]:
            _snack(page, "Debe seleccionar rubro", False)
            return
        sugerido = codigo_preview.value.replace("Código sugerido: ", "")
        ok, msg, _new_id = crear_generico(db_path, int(selected_rubro["id"]), nombre_field.value or "", sugerido)
        close(dlg)
        _snack(page, msg, ok)
        if ok and refresh_callback:
            try:
                refresh_callback()
            except Exception as ex:
                print(f"Refresh error tras crear genérico: {ex}")

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Nuevo Genérico", color=ft.Colors.BLUE),
        content=ft.Container(
            content=ft.Column([
                tipo_menu,
                rubro_menu,
                codigo_preview,
                nombre_field,
            ], spacing=10),
            width=520,
            bgcolor=ft.Colors.WHITE,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: close(dlg), style=ft.ButtonStyle(color=ft.Colors.BLUE)),
            ft.ElevatedButton("Crear", icon=ft.Icons.SAVE, on_click=submit, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=ft.Colors.WHITE,
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()

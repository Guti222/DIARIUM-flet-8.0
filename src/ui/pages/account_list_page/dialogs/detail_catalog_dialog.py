import flet as ft
import sqlite3
from data.catalogoOps import (
    actualizar_generico,
    actualizar_rubro,
    actualizar_tipo_cuenta,
    eliminar_generico,
    eliminar_rubro,
    eliminar_tipo_cuenta,
)
from data.models.cuenta import Generico, Rubro, TipoCuenta
from data.obtenerCuentas import obtenerTodasTipoCuentas, obtenerTodosRubroPorTipoCuenta
from src.utils.paths import get_db_path


def _show_snackbar(page: ft.Page, message: str, success: bool = True):
    color = ft.Colors.GREEN if success else ft.Colors.RED
    page.snack_bar = ft.SnackBar(content=ft.Text(message, color=ft.Colors.WHITE), bgcolor=color)
    page.snack_bar.open = True
    page.update()


def _close_dialog(page: ft.Page, dlg: ft.AlertDialog):
    dlg.open = False
    page.update()


def _confirm_delete(page: ft.Page, message: str, on_confirm):
    confirm = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar Eliminación", color=ft.Colors.RED),
        content=ft.Text(message, color=ft.Colors.BLACK),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: _close_dialog(page, confirm), style=ft.ButtonStyle(color=ft.Colors.BLUE)),
            ft.TextButton("Eliminar", on_click=lambda e: on_confirm(confirm), style=ft.ButtonStyle(color=ft.Colors.RED)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=ft.Colors.WHITE,
    )
    page.overlay.append(confirm)
    confirm.open = True
    page.update()


def open_detail_tipo_dialog(page: ft.Page, tipo: TipoCuenta, stats: dict, refresh_callback=None):
    db_path = get_db_path()
    nombre_field = ft.TextField(label="Nombre", value=tipo.nombre_tipo_cuenta, color=ft.Colors.BLACK)
    numero_field = ft.TextField(label="Código", value=tipo.numero_cuenta, color=ft.Colors.BLACK)
    codigo_sugerido_text = ft.Text("", size=12, color=ft.Colors.GREY_700)

    def sugerir_codigo_tipo() -> str:
        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT numero_cuenta FROM tipo_cuenta")
                rows = [r[0] for r in cur.fetchall() if r and r[0]]
        except Exception:
            rows = []

        usados = set()
        for codigo in rows:
            partes = str(codigo).split(".")
            if len(partes) == 4:
                try:
                    usados.add(int(partes[0]))
                except ValueError:
                    continue

        n = 1
        while n in usados:
            n += 1
        return f"{n}.0.0.000"

    def actualizar_sugerido():
        sugerido = sugerir_codigo_tipo()
        codigo_sugerido_text.value = f"Sugerido: {sugerido}" if sugerido else ""

    actualizar_sugerido()

    def save(_):
        ok = actualizar_tipo_cuenta(db_path, tipo.id_tipo_cuenta, nombre_field.value, numero_field.value)
        _close_dialog(page, dlg)
        _show_snackbar(page, "Tipo actualizado" if ok else "No se pudo actualizar", ok)
        if ok and refresh_callback:
            try:
                refresh_callback()
            except Exception as ex:
                print(f"Error refrescando tras actualizar tipo: {ex}")

    def do_delete(confirm_dlg):
        ok, msg = eliminar_tipo_cuenta(db_path, tipo.id_tipo_cuenta)
        _close_dialog(page, confirm_dlg)
        _close_dialog(page, dlg)
        _show_snackbar(page, msg, ok)
        if ok and refresh_callback:
            try:
                refresh_callback()
            except Exception as ex:
                print(f"Error refrescando tras eliminar tipo: {ex}")

    def ask_delete(_):
        _confirm_delete(page, f"¿Eliminar el tipo {tipo.numero_cuenta} - {tipo.nombre_tipo_cuenta}?", do_delete)

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Detalle de Tipo de Cuenta", color=ft.Colors.BLUE),
        content=ft.Container(
            content=ft.Column([
                ft.Text(f"Rubros: {stats.get('rubros', 0)} | Genéricos: {stats.get('genericos', 0)} | Cuentas: {stats.get('cuentas', 0)}", color=ft.Colors.BLACK),
                numero_field,
                ft.Row([
                    ft.TextButton("Usar sugerido", on_click=lambda e: (setattr(numero_field, "value", codigo_sugerido_text.value.replace("Sugerido: ", "")), page.update())),
                    codigo_sugerido_text,
                ], spacing=10),
                nombre_field,
            ], spacing=10),
            width=420,
            bgcolor=ft.Colors.WHITE,
        ),
        actions=[
            ft.TextButton("Cerrar", on_click=lambda e: _close_dialog(page, dlg), style=ft.ButtonStyle(color=ft.Colors.BLUE)),
            ft.TextButton("Eliminar", on_click=ask_delete, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=save, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=ft.Colors.WHITE,
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()


def open_detail_rubro_dialog(page: ft.Page, rubro: Rubro, stats: dict, refresh_callback=None):
    db_path = get_db_path()
    nombre_field = ft.TextField(label="Nombre", value=rubro.nombre_rubro, color=ft.Colors.BLACK)
    numero_field = ft.TextField(label="Código", value=rubro.numero_cuenta, color=ft.Colors.BLACK)
    tipos = obtenerTodasTipoCuentas(db_path)
    selected_tipo_id = rubro.id_tipo_cuenta or getattr(rubro.tipo_cuenta, "id_tipo_cuenta", None)
    tipo_dropdown = ft.Dropdown(
        label="Tipo",
        options=[
            ft.dropdown.Option(
                key=str(t.id_tipo_cuenta),
                text=f"{t.numero_cuenta} - {t.nombre_tipo_cuenta}"
            ) for t in tipos
        ],
        value=str(selected_tipo_id) if selected_tipo_id is not None else None,
        bgcolor=ft.Colors.WHITE,
        color=ft.Colors.BLACK,
        text_style=ft.TextStyle(color=ft.Colors.BLACK),
        width=360,
    )
    codigo_sugerido_text = ft.Text("", size=12, color=ft.Colors.GREY_700)

    def sugerir_codigo_rubro(tipo_obj: TipoCuenta | None):
        if not tipo_obj:
            return ""
        parts = (tipo_obj.numero_cuenta or "").split(".")
        seg1 = parts[0] if parts and parts[0] else str(tipo_obj.id_tipo_cuenta)
        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT numero_cuenta FROM rubro WHERE id_tipo_cuenta = ?", (int(tipo_obj.id_tipo_cuenta),))
                rows = [r[0] for r in cur.fetchall() if r and r[0]]
        except Exception:
            rows = []

        usados = set()
        for codigo in rows:
            p = str(codigo).split(".")
            if len(p) == 4 and p[0] == str(seg1):
                try:
                    usados.add(int(p[1]))
                except ValueError:
                    continue

        n = 1
        while n in usados:
            n += 1
        return f"{seg1}.{n}.0.000"

    def actualizar_sugerido():
        tipo_id = tipo_dropdown.value
        tipo_obj = next((t for t in tipos if str(t.id_tipo_cuenta) == str(tipo_id)), None)
        sugerido = sugerir_codigo_rubro(tipo_obj)
        codigo_sugerido_text.value = f"Sugerido: {sugerido}" if sugerido else ""

    def on_tipo_change(e):
        tipo_id = e.control.value or tipo_dropdown.value
        tipo_dropdown.value = tipo_id
        actualizar_sugerido()
        if codigo_sugerido_text.value:
            numero_field.value = codigo_sugerido_text.value.replace("Sugerido: ", "")
        page.update()

    tipo_dropdown.on_change = on_tipo_change
    tipo_dropdown.on_text_change = on_tipo_change
    actualizar_sugerido()

    def save(_):
        tipo_id = int(tipo_dropdown.value) if tipo_dropdown.value else rubro.id_tipo_cuenta
        ok = actualizar_rubro(db_path, rubro.id_rubro, nombre_field.value, numero_field.value, id_tipo_cuenta=tipo_id)
        _close_dialog(page, dlg)
        _show_snackbar(page, "Rubro actualizado" if ok else "No se pudo actualizar", ok)
        if ok and refresh_callback:
            try:
                refresh_callback()
            except Exception as ex:
                print(f"Error refrescando tras actualizar rubro: {ex}")

    def do_delete(confirm_dlg):
        ok, msg = eliminar_rubro(db_path, rubro.id_rubro)
        _close_dialog(page, confirm_dlg)
        _close_dialog(page, dlg)
        _show_snackbar(page, msg, ok)
        if ok and refresh_callback:
            try:
                refresh_callback()
            except Exception as ex:
                print(f"Error refrescando tras eliminar rubro: {ex}")

    def ask_delete(_):
        _confirm_delete(page, f"¿Eliminar el rubro {rubro.numero_cuenta} - {rubro.nombre_rubro}?", do_delete)

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Detalle de Rubro", color=ft.Colors.BLUE),
        content=ft.Container(
            content=ft.Column([
                tipo_dropdown,
                ft.Text(f"Genéricos: {stats.get('genericos', 0)} | Cuentas: {stats.get('cuentas', 0)}", color=ft.Colors.BLACK),
                numero_field,
                ft.Row([
                    ft.TextButton("Usar sugerido", on_click=lambda e: (setattr(numero_field, "value", codigo_sugerido_text.value.replace("Sugerido: ", "")), page.update())),
                    codigo_sugerido_text,
                ], spacing=10),
                nombre_field,
            ], spacing=10),
            width=420,
            bgcolor=ft.Colors.WHITE,
        ),
        actions=[
            ft.TextButton("Cerrar", on_click=lambda e: _close_dialog(page, dlg), style=ft.ButtonStyle(color=ft.Colors.BLUE)),
            ft.TextButton("Eliminar", on_click=ask_delete, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=save, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=ft.Colors.WHITE,
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()


def open_detail_generico_dialog(page: ft.Page, generico: Generico, stats: dict, refresh_callback=None):
    db_path = get_db_path()
    nombre_field = ft.TextField(label="Nombre", value=generico.nombre_generico, color=ft.Colors.BLACK)
    numero_field = ft.TextField(label="Código", value=generico.numero_cuenta, color=ft.Colors.BLACK)
    tipos = obtenerTodasTipoCuentas(db_path)
    selected_tipo_id = getattr(getattr(generico.rubro, "tipo_cuenta", None), "id_tipo_cuenta", None)
    selected_rubro_id = getattr(generico.rubro, "id_rubro", None)

    tipo_dropdown = ft.Dropdown(
        label="Tipo",
        options=[
            ft.dropdown.Option(
                key=str(t.id_tipo_cuenta),
                text=f"{t.numero_cuenta} - {t.nombre_tipo_cuenta}",
            ) for t in tipos
        ],
        value=str(selected_tipo_id) if selected_tipo_id is not None else None,
        bgcolor=ft.Colors.WHITE,
        color=ft.Colors.BLACK,
        text_style=ft.TextStyle(color=ft.Colors.BLACK),
        width=360,
    )

    rubro_dropdown = ft.Dropdown(
        label="Rubro",
        options=[],
        value=str(selected_rubro_id) if selected_rubro_id is not None else None,
        bgcolor=ft.Colors.WHITE,
        color=ft.Colors.BLACK,
        text_style=ft.TextStyle(color=ft.Colors.BLACK),
        width=360,
    )

    codigo_sugerido_text = ft.Text("", size=12, color=ft.Colors.GREY_700)

    def cargar_rubros(tipo_id: int | None):
        rubros = obtenerTodosRubroPorTipoCuenta(db_path, int(tipo_id)) if tipo_id else []
        rubro_dropdown.options = [
            ft.dropdown.Option(
                key=str(r.id_rubro),
                text=f"{r.numero_cuenta} - {r.nombre_rubro}",
            ) for r in rubros
        ]
        if rubros:
            if not rubro_dropdown.value or not any(str(r.id_rubro) == str(rubro_dropdown.value) for r in rubros):
                rubro_dropdown.value = str(rubros[0].id_rubro)
        return rubros

    def sugerir_codigo_generico(rubro_obj: Rubro | None, tipo_obj: TipoCuenta | None):
        if not rubro_obj:
            return ""
        parts = (rubro_obj.numero_cuenta or "").split(".")
        if len(parts) >= 2:
            seg1, seg2 = parts[0], parts[1]
        else:
            seg1 = str(tipo_obj.id_tipo_cuenta) if tipo_obj else "0"
            seg2 = str(rubro_obj.id_rubro)

        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT numero_cuenta FROM generico WHERE id_rubro = ?", (int(rubro_obj.id_rubro),))
                rows = [r[0] for r in cur.fetchall() if r and r[0]]
        except Exception:
            rows = []

        usados = set()
        for codigo in rows:
            p = str(codigo).split(".")
            if len(p) == 4 and p[0] == str(seg1) and p[1] == str(seg2):
                try:
                    usados.add(int(p[2]))
                except ValueError:
                    continue

        n = 1
        while n in usados:
            n += 1
        return f"{seg1}.{seg2}.{n}.000"

    def actualizar_sugerido():
        tipo_id = tipo_dropdown.value
        tipo_obj = next((t for t in tipos if str(t.id_tipo_cuenta) == str(tipo_id)), None)
        rubros = obtenerTodosRubroPorTipoCuenta(db_path, int(tipo_id)) if tipo_id else []
        rubro_obj = next((r for r in rubros if str(r.id_rubro) == str(rubro_dropdown.value)), None)
        sugerido = sugerir_codigo_generico(rubro_obj, tipo_obj)
        codigo_sugerido_text.value = f"Sugerido: {sugerido}" if sugerido else ""

    def on_tipo_change(e):
        tipo_id = e.control.value or tipo_dropdown.value
        tipo_dropdown.value = tipo_id
        rubros = cargar_rubros(int(tipo_id)) if tipo_id else []
        if rubros:
            rubro_dropdown.value = str(rubros[0].id_rubro)
        actualizar_sugerido()
        if codigo_sugerido_text.value:
            numero_field.value = codigo_sugerido_text.value.replace("Sugerido: ", "")
        page.update()

    def on_rubro_change(e):
        rubro_id = e.control.value or rubro_dropdown.value
        rubro_dropdown.value = rubro_id
        actualizar_sugerido()
        if codigo_sugerido_text.value:
            numero_field.value = codigo_sugerido_text.value.replace("Sugerido: ", "")
        page.update()

    tipo_dropdown.on_change = on_tipo_change
    tipo_dropdown.on_text_change = on_tipo_change
    rubro_dropdown.on_change = on_rubro_change
    rubro_dropdown.on_text_change = on_rubro_change
    cargar_rubros(int(tipo_dropdown.value)) if tipo_dropdown.value else None
    actualizar_sugerido()

    def save(_):
        rubro_id = int(rubro_dropdown.value) if rubro_dropdown.value else getattr(generico.rubro, "id_rubro", None)
        ok = actualizar_generico(db_path, generico.id_generico, nombre_field.value, numero_field.value, id_rubro=rubro_id)
        _close_dialog(page, dlg)
        _show_snackbar(page, "Genérico actualizado" if ok else "No se pudo actualizar", ok)
        if ok and refresh_callback:
            try:
                refresh_callback()
            except Exception as ex:
                print(f"Error refrescando tras actualizar genérico: {ex}")

    def do_delete(confirm_dlg):
        ok, msg = eliminar_generico(db_path, generico.id_generico)
        _close_dialog(page, confirm_dlg)
        _close_dialog(page, dlg)
        _show_snackbar(page, msg, ok)
        if ok and refresh_callback:
            try:
                refresh_callback()
            except Exception as ex:
                print(f"Error refrescando tras eliminar genérico: {ex}")

    def ask_delete(_):
        _confirm_delete(page, f"¿Eliminar el genérico {generico.numero_cuenta} - {generico.nombre_generico}?", do_delete)

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Detalle de Genérico", color=ft.Colors.BLUE),
        content=ft.Container(
            content=ft.Column([
                tipo_dropdown,
                rubro_dropdown,
                ft.Text(f"Cuentas: {stats.get('cuentas', 0)}", color=ft.Colors.BLACK),
                numero_field,
                ft.Row([
                    ft.TextButton("Usar sugerido", on_click=lambda e: (setattr(numero_field, "value", codigo_sugerido_text.value.replace("Sugerido: ", "")), page.update())),
                    codigo_sugerido_text,
                ], spacing=10),
                nombre_field,
            ], spacing=10),
            width=420,
            bgcolor=ft.Colors.WHITE,
        ),
        actions=[
            ft.TextButton("Cerrar", on_click=lambda e: _close_dialog(page, dlg), style=ft.ButtonStyle(color=ft.Colors.BLUE)),
            ft.TextButton("Eliminar", on_click=ask_delete, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=save, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=ft.Colors.WHITE,
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()

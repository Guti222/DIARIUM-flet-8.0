import flet as ft
import sqlite3
from src.utils.paths import get_db_path
from data.models.cuenta import CuentaContable
from data.actualizarCuenta import actualizar_cuenta_contable
from data.obtenerCuentas import (
    obtenerTodasTipoCuentas,
    obtenerTodosRubroPorTipoCuenta,
    obtenerTodosGenericoPorRubro,
)

def open_edit_account_dialog(page: ft.Page, cuenta: CuentaContable, refresh_callback: callable = None, parent_dialog: ft.AlertDialog | None = None):
    if parent_dialog:
        parent_dialog.open = False
    page.update()

    db_path = get_db_path()
    tipos = obtenerTodasTipoCuentas(db_path)

    codigo_field = ft.TextField(label="Código", value=str(cuenta.codigo_cuenta), width=160,border_color=ft.Colors.BLUE, color=ft.Colors.BLACK)
    nombre_field = ft.TextField(label="Nombre", value=cuenta.nombre_cuenta, width=320,border_color=ft.Colors.BLUE, color=ft.Colors.BLACK)
    descripcion_field = ft.TextField(label="Descripción", value=cuenta.descripcion, multiline=True, min_lines=2, max_lines=4, width=320, border_color=ft.Colors.BLUE, color=ft.Colors.BLACK)
    codigo_sugerido_text = ft.Text("", size=12, color=ft.Colors.GREY_700)

    selected_tipo = {"id": None, "nombre": None}
    selected_rubro = {"id": None, "nombre": None}
    selected_generico = {"id": None, "nombre": None}

    def build_menu(label: str, color_disabled=ft.Colors.GREY):
        return ft.PopupMenuButton(
            content=ft.Container(
                content=ft.Row([
                    ft.Text(label, color=color_disabled),
                    ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=color_disabled)
                ]),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                bgcolor=ft.Colors.WHITE,
            ),
            items=[],
            disabled=True
        )

    tipo_menu = build_menu("Seleccione tipo de cuenta")
    rubro_menu = build_menu("Seleccione rubro")
    generico_menu = build_menu("Seleccione genérico")

    tipo_menu.items = [
        ft.PopupMenuItem(
            content=ft.Text(t.nombre_tipo_cuenta, color=ft.Colors.BLACK),
            data={"id": t.id_tipo_cuenta, "nombre": t.nombre_tipo_cuenta},
            on_click=lambda e: select_tipo(e.control.data)
        ) for t in tipos
    ]
    tipo_menu.disabled = False
    tipo_menu.content.border = ft.border.all(1, ft.Colors.BLUE)
    for c in tipo_menu.content.content.controls:
        if isinstance(c, (ft.Text, ft.Icon)):
            c.color = ft.Colors.BLACK

    def reset_rubro():
        rubro_menu.items = []
        rubro_menu.disabled = True
        rubro_menu.content.border = ft.border.all(1, ft.Colors.GREY_400)
        rubro_menu.content.content.controls[0].value = "Seleccione rubro"
        rubro_menu.content.content.controls[0].color = ft.Colors.GREY
        selected_rubro.update({"id": None, "nombre": None})
        reset_generico()

    def reset_generico():
        generico_menu.items = []
        generico_menu.disabled = True
        generico_menu.content.border = ft.border.all(1, ft.Colors.GREY_400)
        generico_menu.content.content.controls[0].value = "Seleccione genérico"
        generico_menu.content.content.controls[0].color = ft.Colors.GREY
        selected_generico.update({"id": None, "nombre": None})
        codigo_sugerido_text.value = ""

    def select_tipo(data):
        selected_tipo.update(data)
        tipo_menu.content.content.controls[0].value = data["nombre"]
        tipo_menu.content.border = ft.border.all(1, ft.Colors.BLUE)
        reset_rubro()
        rubros = obtenerTodosRubroPorTipoCuenta(db_path, int(data["id"]))
        rubro_menu.items = [
            ft.PopupMenuItem(
                content=ft.Text(r.nombre_rubro, color=ft.Colors.BLACK),
                data={"id": r.id_rubro, "nombre": r.nombre_rubro},
                on_click=lambda e: select_rubro(e.control.data)
            ) for r in rubros
        ]
        rubro_menu.disabled = False
        rubro_menu.content.border = ft.border.all(1, ft.Colors.BLUE)
        rubro_menu.content.content.controls[0].color = ft.Colors.BLACK
        page.update()

    def select_rubro(data):
        selected_rubro.update(data)
        rubro_menu.content.content.controls[0].value = data["nombre"]
        rubro_menu.content.border = ft.border.all(1, ft.Colors.BLUE)
        reset_generico()
        genericos = obtenerTodosGenericoPorRubro(db_path, int(data["id"]))
        generico_menu.items = [
            ft.PopupMenuItem(
                content=ft.Text(g.nombre_generico, color=ft.Colors.BLACK),
                data={"id": g.id_generico, "nombre": g.nombre_generico},
                on_click=lambda e: select_generico(e.control.data)
            ) for g in genericos
        ]
        generico_menu.disabled = False
        generico_menu.content.border = ft.border.all(1, ft.Colors.BLUE)
        generico_menu.content.content.controls[0].color = ft.Colors.BLACK
        page.update()

    def sugerir_codigo(id_generico: int):
        """Genera el código sugerido usando la lógica de creación (MAX + 1).

        Formato esperado: tipo.rubro.generico.###
        Si no hay coincidencia con formato, inicia en .001.
        """
        if not (selected_tipo["id"] and selected_rubro["id"]):
            codigo_sugerido_text.value = "Seleccione tipo y rubro primero"
            page.update()
            return

        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # Obtener el máximo código existente para este genérico
            cur.execute("SELECT MAX(codigo_cuenta) FROM cuenta_contable WHERE id_generico = ?", (id_generico,))
            ultimo_codigo = cur.fetchone()[0]
        finally:
            try: conn.close()
            except Exception: pass

        tipo_id = selected_tipo['id']
        rubro_id = selected_rubro['id']
        base = f"{tipo_id}.{rubro_id}.{id_generico}"

        if ultimo_codigo:
            partes = str(ultimo_codigo).split('.')
            if len(partes) == 4:
                try:
                    nuevo_numero = int(partes[3]) + 1
                except ValueError:
                    nuevo_numero = 1
                sugerido = f"{partes[0]}.{partes[1]}.{partes[2]}.{nuevo_numero:03d}"
            else:
                # Formato inesperado, reiniciar numeración
                sugerido = f"{base}.001"
        else:
            # Primera cuenta para este genérico
            sugerido = f"{base}.001"

        codigo_sugerido_text.value = f"Sugerido: {sugerido}"
        # Sólo pre-rellenar si realmente cambia de genérico respecto al original
        if cuenta.id_generico != id_generico:
            codigo_field.value = sugerido
        page.update()

    def select_generico(data):
        selected_generico.update(data)
        generico_menu.content.content.controls[0].value = data["nombre"]
        generico_menu.content.border = ft.border.all(1, ft.Colors.BLUE)
        sugerir_codigo(int(data["id"]))
        page.update()

    usar_sugerido_btn = ft.TextButton("Usar sugerido", on_click=lambda e: (codigo_field.set_value(codigo_sugerido_text.value.replace("Sugerido: ", "")), page.update()))

    def submit_update(e):
        nuevo_codigo = codigo_field.value.strip()
        nuevo_nombre = nombre_field.value.strip()
        nueva_desc = descripcion_field.value.strip()
        try:
            nuevo_generico = int(selected_generico['id']) if selected_generico['id'] else cuenta.id_generico
        except Exception:
            nuevo_generico = cuenta.id_generico
        ok = actualizar_cuenta_contable(db_path, cuenta.id_cuenta_contable, nuevo_generico, nueva_desc, nuevo_nombre, nuevo_codigo)
        edit_dialog.open = False
        page.update()
        page.snack_bar = ft.SnackBar(content=ft.Text("Cuenta actualizada" if ok else "Error al actualizar cuenta"))
        page.snack_bar.open = True
        page.update()
        if ok:
            if refresh_callback:
                try: refresh_callback()
                except Exception as ex: print(f"Error refresh tras editar: {ex}")
            else:
                page.go("/account-list")

    edit_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Editar Cuenta Contable", color=ft.Colors.BLUE),
        content=ft.Container(
            content=ft.Column([
                ft.Text("Tipo de Cuenta", weight=ft.FontWeight.BOLD,color=ft.Colors.BLACK), tipo_menu,
                ft.Text("Rubro", weight=ft.FontWeight.BOLD,color=ft.Colors.BLACK), rubro_menu,
                ft.Text("Genérico", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK), generico_menu,
                ft.Row([codigo_field, usar_sugerido_btn], alignment=ft.MainAxisAlignment.START),
                codigo_sugerido_text,
                nombre_field,
                descripcion_field,
            ], spacing=14),
            width=500,
            padding=20,
            bgcolor=ft.Colors.WHITE,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: (edit_dialog.__setattr__('open', False), page.update())),
            ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=submit_update,bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=ft.Colors.WHITE
    )
    page.overlay.append(edit_dialog)
    edit_dialog.open = True
    page.update()

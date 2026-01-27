import flet as ft
from data.catalogoOps import (
    actualizar_generico,
    actualizar_rubro,
    actualizar_tipo_cuenta,
    eliminar_generico,
    eliminar_rubro,
    eliminar_tipo_cuenta,
)
from data.models.cuenta import Generico, Rubro, TipoCuenta
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
    tipo_text = ft.Text(f"Tipo: {getattr(rubro.tipo_cuenta, 'numero_cuenta', '')} - {getattr(rubro.tipo_cuenta, 'nombre_tipo_cuenta', '')}", color=ft.Colors.BLACK)

    def save(_):
        ok = actualizar_rubro(db_path, rubro.id_rubro, nombre_field.value, numero_field.value)
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
                tipo_text,
                ft.Text(f"Genéricos: {stats.get('genericos', 0)} | Cuentas: {stats.get('cuentas', 0)}", color=ft.Colors.BLACK),
                numero_field,
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
    tipo_text = ft.Text(
        f"Tipo: {getattr(generico.rubro.tipo_cuenta, 'numero_cuenta', '')} - {getattr(generico.rubro.tipo_cuenta, 'nombre_tipo_cuenta', '')}",
        color=ft.Colors.BLACK,
    )
    rubro_text = ft.Text(
        f"Rubro: {getattr(generico.rubro, 'numero_cuenta', '')} - {getattr(generico.rubro, 'nombre_rubro', '')}",
        color=ft.Colors.BLACK,
    )

    def save(_):
        ok = actualizar_generico(db_path, generico.id_generico, nombre_field.value, numero_field.value)
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
                tipo_text,
                rubro_text,
                ft.Text(f"Cuentas: {stats.get('cuentas', 0)}", color=ft.Colors.BLACK),
                numero_field,
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

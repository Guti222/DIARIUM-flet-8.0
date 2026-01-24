import flet as ft
from data.isCuentaUtilizada import is_cuenta_utilizada
from data.models.cuenta import CuentaContable
from .edit_account_dialog import open_edit_account_dialog
from data.eliminarCuenta import eliminar_cuenta_contable
from src.utils.paths import get_db_path

def open_detail_account_dialog(page: ft.Page, cuenta: CuentaContable, refresh_callback: callable = None):
    def close(dlg):
        dlg.open = False
        page.update()

    def confirm_delete():
        detail_dialog.open = False
        confirm = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Eliminación", color=ft.Colors.RED),
            content=ft.Text(f"¿Eliminar cuenta {cuenta.codigo_cuenta} - {cuenta.nombre_cuenta}?", color=ft.Colors.BLACK),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: close(confirm), style=ft.ButtonStyle(color=ft.Colors.BLUE)),
                ft.TextButton("Eliminar", style=ft.ButtonStyle(color=ft.Colors.RED), on_click=lambda e: do_delete(confirm)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=ft.Colors.WHITE
        )
        page.overlay.append(confirm)
        confirm.open = True
        page.update()

    def do_delete(dlg):
        
        if(is_cuenta_utilizada(get_db_path(), cuenta.id_cuenta_contable)):
            close(dlg)
            show_error_dialog("Esta cuenta está en uso y no se puede eliminar.")
            return
        ok = eliminar_cuenta_contable(get_db_path(), cuenta.id_cuenta_contable)
        close(dlg)
        if ok:
            show_snackbar(f"Cuenta {cuenta.codigo_cuenta} eliminada")
            if refresh_callback:
                try: refresh_callback()
                except Exception as ex: print(f"Error refresh tras eliminar: {ex}")
            else:
                page.go("/account-list")
        else:
            show_snackbar("Error eliminando cuenta")

    def show_snackbar(msg: str):
        page.snack_bar = ft.SnackBar(content=ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    def show_error_dialog(msg: str):
        error_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("No se puede eliminar", color=ft.Colors.RED),
            content=ft.Text(msg, color=ft.Colors.BLACK),
            actions=[
                ft.TextButton(
                    "Entendido",
                    on_click=lambda e: close(error_dialog),
                    style=ft.ButtonStyle(color=ft.Colors.BLUE)
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=ft.Colors.WHITE
        )
        page.dialog = error_dialog
        error_dialog.open = True
        page.update()

    detail_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(f"Detalles de Cuenta: {cuenta.codigo_cuenta}", color=ft.Colors.BLUE),
        content=ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text("Código:", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.BLACK), ft.Text(cuenta.codigo_cuenta, size=14, color=ft.Colors.BLACK)]),
                        ft.Row([ft.Text("Nombre:", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.BLACK), ft.Text(cuenta.nombre_cuenta, size=14, color=ft.Colors.BLACK)]),
                        ft.Row([ft.Text("Descripción:", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.BLACK), ft.Text(getattr(cuenta, "descripcion", ""), size=14, color=ft.Colors.BLACK)]),
                        ft.Row([ft.Text("Tipo de Cuenta:", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.BLACK), ft.Text(cuenta.nombre_tipo_cuenta, size=14, color=ft.Colors.BLACK)]),
                        ft.Row([ft.Text("Rubro:", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.BLACK), ft.Text(cuenta.nombre_rubro, size=14, color=ft.Colors.BLACK)]),
                        ft.Row([ft.Text("Genérico:", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.BLACK), ft.Text(cuenta.nombre_generico, size=14, color=ft.Colors.BLACK)]),
                    ], spacing=10),
                    padding=15,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    margin=10
                )
            ]),
            width=420,
            bgcolor=ft.Colors.WHITE
        ),
        actions=[
            ft.TextButton("Volver", icon=ft.Icons.ARROW_BACK,style=ft.ButtonStyle(color=ft.Colors.BLUE), on_click=lambda e: close(detail_dialog)),
            ft.TextButton("Editar", icon=ft.Icons.EDIT,style=ft.ButtonStyle(color=ft.Colors.BLUE), on_click=lambda e: open_edit_account_dialog(page, cuenta, refresh_callback, parent_dialog=detail_dialog)),
            ft.TextButton("Eliminar", icon=ft.Icons.DELETE, style=ft.ButtonStyle(color=ft.Colors.RED), on_click=lambda e: confirm_delete()),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=ft.Colors.WHITE
    )
    page.overlay.append(detail_dialog)
    detail_dialog.open = True
    page.update()

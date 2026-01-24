import flet as ft
from data.models.cuenta import CuentaContable
from src.ui.pages.account_list_page.dialogs.detail_account_dialog import open_detail_account_dialog

def create_item_account(cuenta: CuentaContable, page: ft.Page, refresh_callback: callable = None, row_index: int = 0) -> ft.Card:

    def show_account_detail(e):
        open_detail_account_dialog(page, cuenta, refresh_callback)

    # Estilo tipo tabla: un borde exterior por fila y separadores verticales
    row_bg = ft.Colors.WHITE if (row_index % 2) == 0 else ft.Colors.BLUE_50
    outer_border = ft.border.all(1, ft.Colors.GREY_200)
    separator = ft.Container(width=1, bgcolor=ft.Colors.GREY_200)

    def cell(content, expand=1, padding=12):
        return ft.Container(
            content=content,
            padding=padding,
            expand=expand,
        )

    return ft.Card(
        content=ft.Container(
            content=ft.Row(
                [
                    cell(ft.Text(cuenta.codigo_cuenta, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS), expand=1),
                    separator,
                    cell(ft.Text(cuenta.nombre_cuenta, size=12, color=ft.Colors.BLACK, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS), expand=3),
                    separator,
                    cell(ft.Text(cuenta.nombre_tipo_cuenta, size=12, color=ft.Colors.BLACK, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS), expand=2),
                    separator,
                    cell(ft.Text(cuenta.nombre_rubro, size=12, color=ft.Colors.BLACK, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS), expand=2),
                    separator,
                    cell(ft.Text(cuenta.nombre_generico, size=12, color=ft.Colors.BLACK, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS), expand=2),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=0,
            expand=True,
            on_click=show_account_detail,
            ink=True,
            bgcolor=row_bg,
            border=outer_border
        ),
        margin=ft.margin.only(bottom=0),
    )
            # on_click=show_account_detail,
import flet as ft
from data.models.cuenta import Generico, Rubro, TipoCuenta
from src.ui.pages.account_list_page.dialogs.detail_catalog_dialog import (
    open_detail_generico_dialog,
    open_detail_rubro_dialog,
    open_detail_tipo_dialog,
)


def _row_card(cells, on_click, row_index: int):
    row_bg = ft.Colors.WHITE if (row_index % 2) == 0 else ft.Colors.BLUE_50
    separator = ft.Container(width=1, bgcolor=ft.Colors.GREY_200)
    outer_border = ft.border.all(1, ft.Colors.GREY_200)

    def cell(content, expand=1, padding=12):
        return ft.Container(content=content, padding=padding, expand=expand)

    interleaved = []
    for idx, c in enumerate(cells):
        interleaved.append(cell(c["content"], expand=c.get("expand", 1)))
        if idx < len(cells) - 1:
            interleaved.append(separator)

    return ft.Card(
        content=ft.Container(
            content=ft.Row(interleaved, vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            padding=0,
            expand=True,
            on_click=on_click,
            ink=True,
            bgcolor=row_bg,
            border=outer_border,
        ),
        margin=ft.margin.only(bottom=0),
    )


def create_item_tipo(tipo: TipoCuenta, page: ft.Page, refresh_callback=None, row_index: int = 0, rubro_count: int = 0, generico_count: int = 0, cuenta_count: int = 0):
    def show_detail(_):
        stats = {"rubros": rubro_count, "genericos": generico_count, "cuentas": cuenta_count}
        open_detail_tipo_dialog(page, tipo, stats, refresh_callback)

    cells = [
        {"content": ft.Text(tipo.numero_cuenta, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)},
        {"content": ft.Text(tipo.nombre_tipo_cuenta, size=12, color=ft.Colors.BLACK), "expand": 3},
        {"content": ft.Text(str(rubro_count), size=12, color=ft.Colors.BLACK)},
        {"content": ft.Text(str(generico_count), size=12, color=ft.Colors.BLACK)},
        {"content": ft.Text(str(cuenta_count), size=12, color=ft.Colors.BLACK)},
    ]
    return _row_card(cells, show_detail, row_index)


def create_item_rubro(rubro: Rubro, page: ft.Page, refresh_callback=None, row_index: int = 0, generico_count: int = 0, cuenta_count: int = 0):
    def show_detail(_):
        stats = {"genericos": generico_count, "cuentas": cuenta_count}
        open_detail_rubro_dialog(page, rubro, stats, refresh_callback)

    tipo_label = f"{getattr(rubro.tipo_cuenta, 'numero_cuenta', '')} - {getattr(rubro.tipo_cuenta, 'nombre_tipo_cuenta', '')}"
    cells = [
        {"content": ft.Text(rubro.numero_cuenta, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)},
        {"content": ft.Text(rubro.nombre_rubro, size=12, color=ft.Colors.BLACK), "expand": 3},
        {"content": ft.Text(tipo_label, size=12, color=ft.Colors.BLACK), "expand": 2},
        {"content": ft.Text(str(generico_count), size=12, color=ft.Colors.BLACK)},
        {"content": ft.Text(str(cuenta_count), size=12, color=ft.Colors.BLACK)},
    ]
    return _row_card(cells, show_detail, row_index)


def create_item_generico(generico: Generico, page: ft.Page, refresh_callback=None, row_index: int = 0, cuenta_count: int = 0):
    def show_detail(_):
        stats = {"cuentas": cuenta_count}
        open_detail_generico_dialog(page, generico, stats, refresh_callback)

    tipo_label = f"{getattr(generico.rubro.tipo_cuenta, 'numero_cuenta', '')} - {getattr(generico.rubro.tipo_cuenta, 'nombre_tipo_cuenta', '')}"
    rubro_label = f"{getattr(generico.rubro, 'numero_cuenta', '')} - {getattr(generico.rubro, 'nombre_rubro', '')}"
    cells = [
        {"content": ft.Text(generico.numero_cuenta, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)},
        {"content": ft.Text(generico.nombre_generico, size=12, color=ft.Colors.BLACK), "expand": 3},
        {"content": ft.Text(tipo_label, size=12, color=ft.Colors.BLACK), "expand": 2},
        {"content": ft.Text(rubro_label, size=12, color=ft.Colors.BLACK), "expand": 2},
        {"content": ft.Text(str(cuenta_count), size=12, color=ft.Colors.BLACK)},
    ]
    return _row_card(cells, show_detail, row_index)

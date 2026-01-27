import flet as ft
import urllib.parse

from data.models.cuenta import TipoCuenta
from data.obtenerCuentas import obtenerTodasTipoCuentas
from data.obternet_plan_cuentas import obtenerTodosPlanesCuentas
from src.ui.components.backgrounds import create_modern_background
from src.ui.pages.account_list_page.account_list import AccountListView
from .create_account_dialog import create_account_dialog
from src.utils.paths import get_db_path
from data.models.plan_cuenta import PlanCuenta
from data.planCuentasOps import crear_plan_cuenta, copiar_cuentas_de_plan
from src.ui.pages.account_list_page.dialogs.create_catalog_dialog import (
    open_create_tipo_dialog,
    open_create_rubro_dialog,
    open_create_generico_dialog,
)
#guty
def header_widget(page: ft.Page, back_action=None):
    def go_back(_e=None):
        # Si se pasó una acción explícita de retorno, usarla primero
        if callable(back_action):
            try:
                back_action()
                return
            except Exception:
                pass
        # Intentar regresar a la ruta anterior si viene en query string
        rt = None
        try:
            if page.route and "?" in page.route:
                query = page.route.split("?", 1)[1]
                params = urllib.parse.parse_qs(query)
                rt = params.get("return_to", [None])[0]
                if rt:
                    rt = urllib.parse.unquote(rt)
        except Exception:
            rt = None
        if rt:
            page.go(rt)
        else:
            try:
                # En la navegación sin router, reconstruir el menú principal manualmente
                from src.ui.pages.menu_page.menu_page import menu_page as menu_view
                page.clean()
                page.add(menu_view(page))
                page.update()
            except Exception:
                page.go("/menu")

    return ft.Container(
        padding=ft.padding.symmetric(vertical=8, horizontal=12),
        content=ft.Row([
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=ft.Colors.WHITE,
                on_click=go_back
            ),
            ft.Text("Plan de Cuentas", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        ], alignment=ft.MainAxisAlignment.START),
        bgcolor=ft.Colors.BLUE_700,
        border_radius=ft.border_radius.all(8),
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=12, color=ft.Colors.BLUE_200, offset=ft.Offset(0, 2)),
    )

def title_widget():
    return ft.Container(
        padding=ft.padding.all(12),
        content=ft.Row([
            ft.Icon(ft.Icons.ACCOUNT_BALANCE, color=ft.Colors.BLUE_800, size=28),
            ft.Text("Lista de Plan de Cuentas", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
        ], spacing=10),
    )

def add_button_widget(page: ft.Page, refresh_callback):
    return ft.FloatingActionButton(
        "Agregar Nueva Cuenta",
        on_click=lambda e: create_account_dialog(page, refresh_callback=refresh_callback),
        icon=ft.Icons.ADD,
        bgcolor=ft.Colors.BLUE,
        foreground_color=ft.Colors.WHITE,
        tooltip="Crear cuenta contable"
    )

def add_tipo_button_widget(page: ft.Page, refresh_callback, plan_id: int | None):
    return ft.FloatingActionButton(
        "Agregar Tipo",
        on_click=lambda e: open_create_tipo_dialog(page, refresh_callback=refresh_callback, plan_id=plan_id),
        icon=ft.Icons.CATEGORY,
        bgcolor=ft.Colors.BLUE,
        foreground_color=ft.Colors.WHITE,
        tooltip="Crear tipo de cuenta",
    )

def add_rubro_button_widget(page: ft.Page, refresh_callback):
    return ft.FloatingActionButton(
        "Agregar Rubro",
        on_click=lambda e: open_create_rubro_dialog(page, refresh_callback=refresh_callback),
        icon=ft.Icons.LIST,
        bgcolor=ft.Colors.BLUE,
        foreground_color=ft.Colors.WHITE,
        tooltip="Crear rubro",
    )

def add_generico_button_widget(page: ft.Page, refresh_callback):
    return ft.FloatingActionButton(
        "Agregar Genérico",
        on_click=lambda e: open_create_generico_dialog(page, refresh_callback=refresh_callback),
        icon=ft.Icons.LABEL,
        bgcolor=ft.Colors.BLUE,
        foreground_color=ft.Colors.WHITE,
        tooltip="Crear genérico",
    )
    
def search_widget( account_list_view:AccountListView):
    search_field = ft.TextField(
        label="Buscar cuenta...",
        prefix_icon=ft.Icons.SEARCH,
        border=ft.border.all(color=ft.Colors.BLUE_200),
        color=ft.Colors.BLACK,
        border_radius=8,
        width=300,
    )
    
    return ft.Container(
        content=ft.Row([
            search_field,
            ft.ElevatedButton(
                "Buscar",
                on_click=lambda e: account_list_view.filter_accounts(search_field.value),
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE,
                icon=ft.Icons.SEARCH,
            )
        ], spacing=10)
    )
    

def filters_widget(account_type, account_list_view: AccountListView, plan_cuentas: list[PlanCuenta], header_container: ft.Container):
    # Construir lista de opciones (valor: nombre_tipo_cuenta)
    optionsTipoCuenta = [ft.dropdown.Option(key="", text="TODOS")]
    optionsTipoCuenta += [
        ft.dropdown.Option(key=account.nombre_tipo_cuenta, text=account.nombre_tipo_cuenta)
        for account in account_type
    ]

    optionsVista = [
        ft.dropdown.Option(key="cuentas", text="Cuentas contables"),
        ft.dropdown.Option(key="tipos", text="Tipos de cuenta"),
        ft.dropdown.Option(key="rubros", text="Rubros"),
        ft.dropdown.Option(key="genericos", text="Genéricos"),
    ]

    def _tipo_on_tipo_change(e):
        val = e.control.value
        try:
            sval = str(val).strip()
        except Exception:
            sval = ""

        if not sval or sval.upper() == "TODOS":
            account_list_view.filter_accounts("", force=True)
        else:
            account_list_view.filter_accounts(sval, force=True)

    def _vista_on_change(e):
        val = e.control.value or "cuentas"
        account_list_view.set_view_mode(val)
        account_list_view.filter_accounts("", force=True)
        try:
            header_container.content = header_account_List_by_mode(val)
            header_container.update()
        except Exception:
            pass

    tipo_dropdown = ft.Dropdown(
        options=optionsTipoCuenta,
        label="Tipo de Cuenta",
        bgcolor=ft.Colors.WHITE,
        color=ft.Colors.BLACK,
        text_style=ft.TextStyle(color=ft.Colors.BLACK),
        width=300,
        value="",
    )
    tipo_dropdown.on_text_change = _tipo_on_tipo_change

    vista_dropdown = ft.Dropdown(
        options=optionsVista,
        label="Vista",
        bgcolor=ft.Colors.WHITE,
        color=ft.Colors.BLACK,
        text_style=ft.TextStyle(color=ft.Colors.BLACK),
        width=300,
        value="cuentas",
    )
    vista_dropdown.on_text_change = _vista_on_change

    return ft.Container(
        padding=ft.padding.all(12),
        bgcolor=ft.Colors.BLUE_50,
        border=ft.border.all(1, ft.Colors.BLUE_200),
        border_radius=8,
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.FILTER_LIST, color=ft.Colors.BLUE_800),
                ft.Text("Filtros", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
            ], spacing=8),
            ft.Row([
                vista_dropdown,
                tipo_dropdown,
                search_widget(account_list_view)
            ], spacing=10)
        ], spacing=8)
    )


def header_account_List():
    return header_account_List_by_mode("cuentas")


def header_account_List_by_mode(view_mode: str):
    header_bg = ft.Colors.BLUE_50
    separator = ft.Container(width=1, bgcolor=ft.Colors.GREY_200)

    def header_cell(text, expand=1):
        return ft.Container(
            content=ft.Text(
                text,
                size=12,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE_900,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            padding=ft.padding.only(left=12, right=12, top=12, bottom=12),
            expand=expand,
            bgcolor=header_bg,
        )

    if view_mode == "tipos":
        cells = [
            header_cell("Código", expand=1),
            separator,
            header_cell("Nombre", expand=3),
            separator,
            header_cell("Rubros", expand=1),
            separator,
            header_cell("Genéricos", expand=1),
            separator,
            header_cell("Cuentas", expand=1),
        ]
    elif view_mode == "rubros":
        cells = [
            header_cell("Código", expand=1),
            separator,
            header_cell("Nombre", expand=3),
            separator,
            header_cell("Tipo", expand=2),
            separator,
            header_cell("Genéricos", expand=1),
            separator,
            header_cell("Cuentas", expand=1),
        ]
    elif view_mode == "genericos":
        cells = [
            header_cell("Código", expand=1),
            separator,
            header_cell("Nombre", expand=3),
            separator,
            header_cell("Tipo", expand=2),
            separator,
            header_cell("Rubro", expand=2),
            separator,
            header_cell("Cuentas", expand=1),
        ]
    else:
        cells = [
            header_cell("Código de Cuenta", expand=1),
            separator,
            header_cell("Nombre", expand=3),
            separator,
            header_cell("Tipo Cuenta", expand=2),
            separator,
            header_cell("Rubro", expand=2),
            separator,
            header_cell("Generico", expand=2),
        ]

    return ft.Container(
        content=ft.Row(cells, spacing=0),
        padding=ft.padding.only(top=10, bottom=0, left=0, right=0),
        border_radius=5,
    )

def account_list_container(account_list_view):
    return ft.Container(
        content=account_list_view.get_view(),
        border=ft.border.all(1, ft.Colors.BLUE_200),
        border_radius=8,
        expand=True,
        bgcolor=ft.Colors.WHITE,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=ft.Colors.BLUE_100, offset=ft.Offset(0, 2)),
    )

def contenido(page: ft.Page, back_action=None, plan_id: int | None = None):
    db_path = get_db_path()
    account_type: list[TipoCuenta] = obtenerTodasTipoCuentas(db_path)
    plan_cuentas: list[PlanCuenta]= obtenerTodosPlanesCuentas(db_path)
    account_list_view = AccountListView(db_path, page)
    if plan_id is not None:
        account_list_view.filter_by_account_plan_id(plan_id)
    header_container = header_account_List()

    return ft.Container(
        content=ft.Column([
            header_widget(page, back_action),
            ft.Row([
                title_widget(),
                ft.Container(expand=True),
                ft.Row([
                    add_tipo_button_widget(page, account_list_view.refresh, plan_id),
                    add_rubro_button_widget(page, account_list_view.refresh),
                    add_generico_button_widget(page, account_list_view.refresh),
                    add_button_widget(page, account_list_view.refresh),
                ], spacing=10)
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            filters_widget(account_type, account_list_view, plan_cuentas, header_container),
            header_container,
            account_list_container(account_list_view)
        ], expand=True, spacing=12),
        padding=ft.padding.all(16),
        expand=True
    )

def account_list_page(page: ft.Page, back_action=None, plan_id: int | None = None):
    return ft.Stack(
        controls=[
            create_modern_background(page),
            contenido(page, back_action, plan_id)
        ],
        expand=True
    )




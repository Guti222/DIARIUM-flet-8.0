import flet as ft
import urllib.parse

from data.models.cuenta import TipoCuenta
from data.obtenerCuentas import obtenerTodasTipoCuentas, obtenerTipoCuentasPorPlanCuenta
from data.obternet_plan_cuentas import obtenerTodosPlanesCuentas
from src.ui.components.backgrounds import create_modern_background
from src.ui.pages.account_list_page.account_list import AccountListView
from .create_account_dialog import create_account_dialog
from src.utils.paths import get_db_path
from data.models.plan_cuenta import PlanCuenta
from src.ui.pages.account_list_page.dialogs.create_catalog_dialog import (
    open_create_tipo_dialog,
    open_create_rubro_dialog,
    open_create_generico_dialog,
)

# --- REFERENCIAS GLOBALES ---
# Usamos estas referencias para poder actualizar la UI desde el hilo de carga
account_view_container = ft.Container(expand=True)
header_container_global = ft.Container()
account_list_view_ref = [None] 

def header_widget(page: ft.Page, back_action=None):
    def go_back(_e=None):
        if callable(back_action):
            try:
                back_action()
                return
            except Exception: pass
        rt = None
        try:
            if page.route and "?" in page.route:
                query = page.route.split("?", 1)[1]
                params = urllib.parse.parse_qs(query)
                rt = params.get("return_to", [None])[0]
                if rt: rt = urllib.parse.unquote(rt)
        except Exception: rt = None

        if rt:
            page.go(rt)
        else:
            try:
                from src.ui.pages.menu_page.menu_page import menu_page as menu_view
                page.clean()
                page.add(menu_view(page))
                page.update()
            except Exception:
                page.go("/menu")

    return ft.Container(
        padding=ft.padding.symmetric(vertical=8, horizontal=12),
        content=ft.Row([
            ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE, on_click=go_back),
            ft.Text("Plan de Cuentas", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        ], alignment=ft.MainAxisAlignment.START),
        bgcolor=ft.Colors.BLUE_700,
        border_radius=8,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=12, color=ft.Colors.BLUE_200, offset=ft.Offset(0, 2)),
    )

def title_widget():
    return ft.Container(
        padding=12,
        content=ft.Row([
            ft.Icon(ft.Icons.ACCOUNT_BALANCE, color=ft.Colors.BLUE_800, size=28),
            ft.Text("Lista de Plan de Cuentas", size=26, weight="bold", color=ft.Colors.BLUE_800),
        ], spacing=10),
    )

# --- BOTONES DE ACCIÓN ---
def add_button_widget(page: ft.Page, refresh_callback, plan_id: int | None):
    return ft.FloatingActionButton(
        "Cuenta",
        on_click=lambda e: create_account_dialog(page, refresh_callback=refresh_callback, plan_id=plan_id),
        icon=ft.Icons.ADD,
        bgcolor=ft.Colors.BLUE,
        foreground_color=ft.Colors.WHITE,
    )

def add_tipo_button_widget(page: ft.Page, refresh_callback, plan_id: int | None):
    return ft.FloatingActionButton("Tipo", on_click=lambda e: open_create_tipo_dialog(page, refresh_callback=refresh_callback, plan_id=plan_id), icon=ft.Icons.CATEGORY, bgcolor=ft.Colors.BLUE, foreground_color=ft.Colors.WHITE)

def add_rubro_button_widget(page: ft.Page, refresh_callback, plan_id: int | None):
    return ft.FloatingActionButton(
        "Rubro",
        on_click=lambda e: open_create_rubro_dialog(page, refresh_callback=refresh_callback, plan_id=plan_id),
        icon=ft.Icons.LIST,
        bgcolor=ft.Colors.BLUE,
        foreground_color=ft.Colors.WHITE,
    )

def add_generico_button_widget(page: ft.Page, refresh_callback, plan_id: int | None):
    return ft.FloatingActionButton(
        "Genérico",
        on_click=lambda e: open_create_generico_dialog(page, refresh_callback=refresh_callback, plan_id=plan_id),
        icon=ft.Icons.LABEL,
        bgcolor=ft.Colors.BLUE,
        foreground_color=ft.Colors.WHITE,
    )

# --- LÓGICA DE ENCABEZADO DINÁMICO ---
def header_account_List_by_mode(view_mode: str):
    header_bg = ft.Colors.BLUE_50
    sep = ft.Container(width=1, bgcolor=ft.Colors.GREY_200)
    def cell(text, exp=1):
        return ft.Container(
            content=ft.Text(text, size=12, weight="bold", color=ft.Colors.BLUE_900), 
            padding=12, expand=exp, bgcolor=header_bg
        )

    if view_mode == "tipos":
        cells = [cell("Código", 1), sep, cell("Nombre", 3), sep, cell("Rubros", 1), sep, cell("Genéricos", 1), sep, cell("Cuentas", 1)]
    elif view_mode == "rubros":
        cells = [cell("Código", 1), sep, cell("Nombre", 3), sep, cell("Tipo", 2), sep, cell("Genéricos", 1), sep, cell("Cuentas", 1)]
    elif view_mode == "genericos":
        cells = [cell("Código", 1), sep, cell("Nombre", 3), sep, cell("Tipo", 2), sep, cell("Rubro", 2), sep, cell("Cuentas", 1)]
    else:
        # Modo por defecto: cuentas
        cells = [cell("Código", 1), sep, cell("Nombre", 3), sep, cell("Tipo Cuenta", 2), sep, cell("Rubro", 2), sep, cell("Generico", 2)]
    
    return ft.Row(cells, spacing=0)

# --- CONTENIDO DE LA PÁGINA ---
def contenido(page: ft.Page, back_action=None, plan_id: int | None = None):
    db_path = get_db_path()

    # Dropdowns de Filtro
    vista_dropdown = ft.Dropdown(
        label="Seleccionar Vista", width=250, bgcolor="white", color="black", value="cuentas",
        options=[
            ft.dropdown.Option("cuentas", "Cuentas contables"),
            ft.dropdown.Option("tipos", "Tipos de cuenta"),
            ft.dropdown.Option("rubros", "Rubros"),
            ft.dropdown.Option("genericos", "Genéricos"),
        ]
    )
    
    tipo_dropdown = ft.Dropdown(label="Filtrar por Tipo", width=250, bgcolor="white", color="black", disabled=True,)
    search_field = ft.TextField(label="Buscar...", width=250, border_radius=8, bgcolor="white")

    account_view_container.alignment = ft.MainAxisAlignment.CENTER
    header_container_global.content = header_account_List_by_mode("cuentas")

    def cargar_datos_background():
        try:
            # Consultas a base de datos
            if plan_id is None:
                tipos_data = obtenerTodasTipoCuentas(db_path)
            else:
                tipos_data = obtenerTipoCuentasPorPlanCuenta(db_path, int(plan_id))
            view = AccountListView(db_path, page, plan_id=plan_id)
            
            if plan_id: 
                view.filter_by_account_plan_id(plan_id)
            
            account_list_view_ref[0] = view

            last_vista = {"value": vista_dropdown.value}
            last_tipo = {"value": ""}

            # --- VINCULAR EVENTOS ---
            
            # 1. Cambio de Vista (Cuentas, Tipos, etc.)
            def change_vista(e):
                mode = (e.control.value or vista_dropdown.value or "cuentas")
                if mode == last_vista["value"]:
                    return
                last_vista["value"] = mode
                # Cambia el modo interno de la lista para que sepa qué datos pintar
                view.set_view_mode(mode)
                # Actualiza el encabezado visualmente
                header_container_global.content = header_account_List_by_mode(mode)
                header_container_global.update()
                page.update()
            
            vista_dropdown.on_change = change_vista
            vista_dropdown.on_text_change = change_vista

            # 2. Filtro de Tipo de Cuenta
            tipo_dropdown.options = [ft.dropdown.Option("", "TODOS")] + [
                ft.dropdown.Option(t.nombre_tipo_cuenta, t.nombre_tipo_cuenta) for t in tipos_data
            ]
            tipo_dropdown.disabled = False
            
            def change_tipo(e):
                val = (e.control.value or tipo_dropdown.value or "")
                if val == last_tipo["value"]:
                    return
                last_tipo["value"] = val
                view.set_tipo_filter(val if val else "")
                page.update()
            
            tipo_dropdown.on_change = change_tipo
            tipo_dropdown.on_text_change = change_tipo

            # Inyectar la vista cargada en el contenedor
            account_view_container.content = view.get_view()
            account_view_container.alignment = None
            page.update()

        except Exception as ex:
            print(f"Error en carga de datos: {ex}")
            account_view_container.content = ft.Text("Error al conectar con la base de datos")
            page.update()

    # Ejecutar carga de datos en el hilo principal para asegurar eventos UI
    cargar_datos_background()

    return ft.Container(
        expand=True, padding=16,
        content=ft.Column([
            header_widget(page, back_action),
            ft.Row([
                title_widget(),
                ft.Container(expand=True),
                ft.Row([
                    add_tipo_button_widget(page, lambda: account_list_view_ref[0].refresh(), plan_id),
                    add_rubro_button_widget(page, lambda: account_list_view_ref[0].refresh(), plan_id),
                    add_generico_button_widget(page, lambda: account_list_view_ref[0].refresh(), plan_id),
                    add_button_widget(page, lambda: account_list_view_ref[0].refresh(), plan_id),
                ], spacing=10)
            ]),
            
            # Panel de Control (Dropdowns y Búsqueda)
            ft.Container(
                padding=12, bgcolor=ft.Colors.BLUE_50, border_radius=8,
                border=ft.border.all(1, ft.Colors.BLUE_200),
                content=ft.Row([
                    vista_dropdown, 
                    tipo_dropdown, 
                    search_field, 
                    ft.ElevatedButton(
                        "Buscar", 
                        icon=ft.Icons.SEARCH, 
                        on_click=lambda _: account_list_view_ref[0].filter_accounts(search_field.value) if account_list_view_ref[0] else None,
                        bgcolor=ft.Colors.BLUE,
                        color="white"
                    )
                ], spacing=10)
            ),
            
            # Encabezado de tabla
            header_container_global,
            
            # Lista de resultados
            ft.Container(
                content=account_view_container, 
                expand=True, 
                border=ft.border.all(1, ft.Colors.BLUE_200), 
                border_radius=8, 
                bgcolor="white"
            )
        ], expand=True, spacing=15)
    )

def account_list_page(page: ft.Page, back_action=None, plan_id: int | None = None):
    return ft.Stack([
        create_modern_background(page), 
        contenido(page, back_action, plan_id)
    ], expand=True)
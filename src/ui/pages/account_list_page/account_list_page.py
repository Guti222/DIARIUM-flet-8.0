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

def add_plan_button_widget(page: ft.Page, refresh_callback):
    def open_dialog(_e=None):
        name_field = ft.TextField(
            label="Nombre del nuevo plan",
            bgcolor=ft.Colors.WHITE,
            color=ft.Colors.BLACK,
            width=400,
        )
        copy_checkbox = ft.Checkbox(
            label="Copiar base del plan General",
            value=True,
        )

        def close(dlg):
            dlg.open = False
            page.update()

        def do_create(_):
            nombre = (name_field.value or "").strip()
            if not nombre:
                # Feedback rápido
                sb = ft.SnackBar(content=ft.Text("Debes ingresar un nombre para el plan"))
                page.overlay.append(sb)
                sb.open = True
                page.update()
                return
            new_id = crear_plan_cuenta(get_db_path(), nombre)
            if new_id is None:
                err = ft.SnackBar(content=ft.Text("El nombre ya existe o no se pudo crear"))
                page.overlay.append(err)
                err.open = True
                page.update()
                return
            if copy_checkbox.value:
                try:
                    copiar_cuentas_de_plan(get_db_path(), 0, new_id)
                except Exception as ex:
                    print(f"Error copiando base del plan General: {ex}")
            close(dlg)
            # Refrescar: reconstruir página para actualizar dropdown y lista
            try:
                refresh_callback()
            except Exception:
                pass
            page.go("/account-list")

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nuevo Plan de Cuentas", color=ft.Colors.BLUE),
            content=ft.Container(
                content=ft.Column([
                    name_field,
                    copy_checkbox,
                ], spacing=10),
                width=460,
                height=100,
                bgcolor=ft.Colors.WHITE,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: close(dlg), style=ft.ButtonStyle(color=ft.Colors.BLUE)),
                ft.TextButton("Crear", on_click=do_create, style=ft.ButtonStyle(color=ft.Colors.GREEN)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=ft.Colors.WHITE,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    return ft.ElevatedButton(
        "Nuevo Plan de Cuentas",
        icon=ft.Icons.LIST_ALT,
        on_click=open_dialog,
        bgcolor=ft.Colors.BLUE,
        color=ft.Colors.WHITE,
        tooltip="Crear plan de cuentas",
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
    

def filters_widget(account_type, account_list_view:AccountListView, plan_cuentas:list[PlanCuenta]):
    # Construir lista de opciones (valor: nombre_tipo_cuenta)
    optionsTipoCuenta = [
        ft.dropdown.Option(key="", text="TODOS")
    ]
    optionsTipoCuenta += [
        ft.dropdown.Option(key=account.nombre_tipo_cuenta, text=account.nombre_tipo_cuenta)
        for account in account_type
    ]
    
    optionsPlanCuenta = [
        ft.dropdown.Option(key="", text="TODOS"),
    ]
    # Usar id como valor (key) y nombre como etiqueta (text)
    optionsPlanCuenta += [
        ft.dropdown.Option(key=str(plan.id_plan_cuenta), text=plan.nombre_plan_cuenta)
        for plan in plan_cuentas
    ]

    def _tipo_on_tipo_change(e):
        val = e.control.value
        # Normalizar el valor: si es vacío o la etiqueta "TODOS", usar cadena vacía
        try:
            sval = str(val).strip()
        except Exception:
            sval = ""

        if not sval or sval.upper() == "TODOS":
            account_list_view.filter_accounts("")
        else:
            account_list_view.filter_accounts(sval)
            
    def _plan_on_tipo_change(e):
        val = e.control.value
        try:
            sval = str(val).strip()
        except Exception:
            sval = ""

        if not sval:
            # Mostrar todos
            account_list_view.filter_by_account_plan_id(None)
        else:
            try:
                id_plan = int(sval)
            except ValueError:
                id_plan = None
            account_list_view.filter_by_account_plan_id(id_plan)

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
    
    plan_cuentas_dropdown = ft.Dropdown(
        options=optionsPlanCuenta,
        label="Plan de cuentas",
        bgcolor=ft.Colors.WHITE,
        color=ft.Colors.BLACK,
        text_style=ft.TextStyle(color=ft.Colors.BLACK),
        width=300,
        value="",  # por defecto mostrar TODOS
    )
    plan_cuentas_dropdown.on_text_change = _plan_on_tipo_change
    

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
                plan_cuentas_dropdown,
                tipo_dropdown,
                search_widget(account_list_view)
            ], spacing=10)
        ], spacing=8)
    )
    
def header_account_List():
    header_bg = ft.Colors.BLUE_50
    separator = ft.Container(width=1, bgcolor=ft.Colors.GREY_200)

    def header_cell(text, expand=1):
        return ft.Container(
            content=ft.Text(text, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
            padding=ft.padding.only(left=12, right=12, top=12, bottom=12),
            expand=expand,
            bgcolor=header_bg,
        )

    return ft.Container(
        content=ft.Row([
            header_cell("Código de Cuenta", expand=1),
            separator,
            header_cell("Nombre", expand=3),
            separator,
            header_cell("Tipo Cuenta", expand=2),
            separator,
            header_cell("Rubro", expand=2),
            separator,
            header_cell("Generico", expand=2),
        ], spacing=0),
        padding=ft.padding.only(top=10, bottom=0, left=0, right=0),
        border_radius=5
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

def contenido(page: ft.Page, back_action=None):
    db_path = get_db_path()
    account_type: list[TipoCuenta] = obtenerTodasTipoCuentas(db_path)
    plan_cuentas: list[PlanCuenta]= obtenerTodosPlanesCuentas(db_path)
    account_list_view = AccountListView(db_path, page)
    return ft.Container(
        content=ft.Column([
            header_widget(page, back_action),
            ft.Row([
                title_widget(),
                ft.Container(expand=True),
                ft.Row([
                    add_plan_button_widget(page, account_list_view.refresh),
                    add_button_widget(page, account_list_view.refresh)
                ], spacing=10)
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            filters_widget(account_type, account_list_view, plan_cuentas),
            header_account_List(),
            account_list_container(account_list_view)
        ], expand=True, spacing=12),
        padding=ft.padding.all(16),
        expand=True
    )

def account_list_page(page: ft.Page, back_action=None):

    return ft.Stack(
        controls=[
            create_modern_background(page),
            contenido(page, back_action)
        ],
        expand=True
    )




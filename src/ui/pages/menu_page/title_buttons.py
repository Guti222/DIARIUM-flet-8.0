import flet as ft
from src.ui.components.widgets.buttons import create_image_button
from src.ui.pages.account_list_page.account_list_page import account_list_page
from data.obternet_plan_cuentas import obtenerTodosPlanesCuentas
from src.utils.paths import get_db_path

# Import opcional con fallback durante la migración
try:
    from src.ui.pages.create_book_page.open_create_dialog import open_create_dialog
except Exception:
    def open_create_dialog(page: ft.Page):
        snack = ft.SnackBar(content=ft.Text("Crear Libro aún en migración"))
        page.overlay.append(snack)
        snack.open = True
        page.update()

try:
    from src.ui.pages.account_list_page.create_account_list_dialog import create_account_list_dialog
except Exception:
    def create_account_list_dialog(page: ft.Page):
        snack = ft.SnackBar(content=ft.Text("Plan de cuentas aún en migración"))
        page.overlay.append(snack)
        snack.open = True
        page.update()

def title_buttons(open_file_explorer_callback=None, page: ft.Page = None):
    """
    Botones del título de la aplicación
    """
    
    def navigate_to_account_list(p: ft.Page, plan_id: int | None = None):
        if p is None:
            return
        try:
            p.clean()
            p.add(account_list_page(p, plan_id=plan_id))
            p.update()
        except Exception as ex:
            snack = ft.SnackBar(content=ft.Text(f"Error abriendo plan de cuentas: {ex}"))
            p.overlay.append(snack)
            snack.open = True
            p.update()

    def open_plan_selector(p: ft.Page):
        if p is None:
            return
        try:
            planes = obtenerTodosPlanesCuentas(get_db_path())
        except Exception as ex:
            planes = []
            snack = ft.SnackBar(content=ft.Text(f"No se pudieron cargar planes: {ex}"))
            p.overlay.append(snack)
            snack.open = True
            p.update()
            return

        lista = ft.ListView(expand=True, spacing=6, padding=8)
        for plan in planes:
            lista.controls.append(
                ft.ListTile(
                    title=ft.Text(plan.nombre_plan_cuenta, color=ft.Colors.BLACK),
                    subtitle=ft.Text(f"ID: {plan.id_plan_cuenta}", color=ft.Colors.GREY_700),
                    trailing=ft.TextButton(
                        "Abrir",
                        on_click=lambda e, pid=plan.id_plan_cuenta: (setattr(selector, "open", False), p.update(), navigate_to_account_list(p, plan_id=pid)),
                        style=ft.ButtonStyle(color=ft.Colors.BLUE),
                    ),
                )
            )

        selector = ft.AlertDialog(
            modal=True,
            title=ft.Text("Planes de Cuentas", color=ft.Colors.BLUE),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Selecciona un plan para ver sus cuentas", color=ft.Colors.BLACK),
                    lista,
                ], spacing=10),
                width=520,
                height=420,
                bgcolor=ft.Colors.WHITE,
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: (setattr(selector, "open", False), p.update()), style=ft.ButtonStyle(color=ft.Colors.BLUE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=ft.Colors.WHITE,
        )

        p.overlay.append(selector)
        selector.open = True
        p.update()

    return  ft.Container(
        padding=ft.padding.only(top=15,right=35),
        content= ft.Column(
            [
                ft.Row(
                    [
                        create_image_button(
                            text="Crear Libro",
                            icon=ft.Icons.BOOK,
                            description="Iniciar un nuevo libro contable",
                            on_click=lambda e: open_create_dialog(e.page),
                        ),
                        create_image_button(
                            text="Cargar Libro",
                            icon=ft.Icons.FOLDER_OPEN,
                            description="Abrir un libro contable existente",
                            on_click=open_file_explorer_callback if open_file_explorer_callback else lambda e: print("FilePicker no disponible")
                        )
                    ]
                ),
                ft.Row(
                    [
                        create_image_button(
                            text="Añadir plan de cuenta",
                            icon=ft.Icons.ACCOUNT_BALANCE,
                            description="Agregar un nuevo plan de cuentas para cuentas contables",
                            on_click=lambda e: create_account_list_dialog(e.page)
                        ),
                        create_image_button(
                            text= "Ver Plan de Cuentas",
                            icon= ft.Icons.VIEW_LIST,
                            description="Visualizar el plan de cuentas completo",
                            on_click=lambda e: open_plan_selector(e.page)
                        )
                    ]
                ),
            ]
        )
    )
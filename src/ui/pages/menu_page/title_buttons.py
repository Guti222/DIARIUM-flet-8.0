import flet as ft
from src.ui.components.widgets.buttons import create_image_button

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
                            on_click=lambda e: page.go("/account-list") if page else print("Navegar a /account-list")
                        )
                    ]
                ),
            ]
        )
    )
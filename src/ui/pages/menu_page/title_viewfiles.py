import flet as ft
import urllib.parse
from src.ui.components.widgets.book_card import book_card

# Importaciones de datos con fallback durante migración
try:
    from data.models.libro import LibroDiario  # noqa: F401
    from data.obtenerLibros import obtenerTodosLibros
    from data.eliminarLibro import eliminar_libro_diario
    from src.utils.paths import get_db_path
    DATA_AVAILABLE = True
except Exception:
    DATA_AVAILABLE = False


def title_viewfiles(page: ft.Page | None = None):
    """Return a container with a ListView of recently opened books.

    If `page` is provided, clicking a book will navigate to the book journal view.
    Includes live refresh after deletion to avoid stale entries.
    """

    list_view = ft.ListView(
        expand=True,
        padding=12,
        auto_scroll=True,
        controls=[],
    )

    def render_list():
        libros = []
        if DATA_AVAILABLE:
            try:
                libros = obtenerTodosLibros(get_db_path())
            except Exception as ex:
                # Mostrar mensaje si hay error consultando datos
                print(f"Error cargando libros: {ex}")
        controls: list[ft.Control] = []
        if libros:
            for libro in libros:
                # Acción de navegación al hacer click en el contenedor
                def _go_to_libro(e, l=libro):
                    # Navegar por ID para evitar inserciones duplicadas
                    page.go(f"/book-journal?libro_id={l.id_libro_diario}")

                # Acción de eliminar libro (con confirmación y refresco in-place)
                def _confirm_delete(_e, l=libro):
                    def _close(dlg):
                        dlg.open = False
                        page.update()

                    def _do_delete(_):
                        ok = False
                        if DATA_AVAILABLE:
                            ok = eliminar_libro_diario(get_db_path(), l.id_libro_diario)
                        _close(confirm)
                        if ok:
                            snack = ft.SnackBar(content=ft.Text("Libro eliminado correctamente"))
                            page.overlay.append(snack)
                            snack.open = True
                            # Refrescar la lista inmediatamente para evitar entradas obsoletas
                            render_list()
                            list_view.update()
                        else:
                            err = ft.SnackBar(content=ft.Text("Error eliminando el libro" if DATA_AVAILABLE else "Datos no disponibles durante migración"))
                            page.overlay.append(err)
                            err.open = True
                        page.update()

                    confirm = ft.AlertDialog(
                        modal=True,
                        title=ft.Text("Confirmar Eliminación", color=ft.Colors.RED),
                        content=ft.Text(
                            f"¿Eliminar el libro {l.nombre_empresa} - {l.ano}/{l.id_mes} y todos sus asientos y líneas?",
                            color=ft.Colors.BLACK,
                        ),
                        actions=[
                            ft.TextButton("Cancelar", on_click=lambda e: _close(confirm), style=ft.ButtonStyle(color=ft.Colors.BLUE)),
                            ft.TextButton("Eliminar", on_click=_do_delete, style=ft.ButtonStyle(color=ft.Colors.RED)),
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                        bgcolor=ft.Colors.WHITE,
                    )
                    page.open(confirm)
                    page.update()

                card = book_card(libro, on_delete=_confirm_delete)

                if page is not None:
                    wrapper = ft.Container(content=card, on_click=_go_to_libro, padding=8)
                else:
                    wrapper = ft.Container(content=card, padding=8)
                controls.append(wrapper)
        else:
            msg = "No hay libros recientes" if DATA_AVAILABLE else "Datos en migración: lista no disponible"
            controls.append(ft.Text(msg, size=16))
        list_view.controls = controls

    # Inicializar la lista
    render_list()

    return ft.Container(
        expand=True,
        content=ft.Column(
            [
                ft.Text(
                    "Archivos abiertos recientemente:",
                    size=30,
                    color=ft.Colors.BLACK,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(
                    expand=True,
                    width=2000,
                    border=ft.border.all(1, ft.Colors.BLUE),
                    border_radius=10,
                    bgcolor=ft.Colors.BLUE_50,
                    content=list_view,
                ),
            ],
            expand=True,
        ),
    )
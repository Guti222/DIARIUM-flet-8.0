import flet as ft
from types import SimpleNamespace

# Tkinter para diálogos nativos
try:
    import tkinter as tk
    from tkinter import filedialog
except Exception:
    tk = None
    filedialog = None

from src.ui.components.backgrounds import create_modern_background
from src.ui.pages.menu_page.title_buttons import title_buttons
from src.ui.pages.menu_page.title_viewfiles import title_viewfiles
from src.ui.pages.menu_page.title_menu import titlemenu
from src.ui.pages.book_journal_page.book_journal_page import book_journal_page


def menu_page(page: ft.Page):
    # ✅ Función para manejar la selección de archivos (Tkinter)
    def pick_file_with_tk() -> SimpleNamespace | None:
        if filedialog is None:
            show_snack_bar("Tkinter no está disponible en este entorno")
            return None
        root = None
        try:
            root = tk.Tk()
            root.withdraw()
            # Forzar que el diálogo salga al frente
            try:
                root.attributes('-topmost', True)
                root.update()
            except Exception:
                pass
            path = filedialog.askopenfilename(
                title="Seleccionar libro contable Excel",
                filetypes=[("Excel", "*.xlsx *.xls")]
            )
            if not path:
                return None
            from pathlib import Path
            p = Path(path)
            return SimpleNamespace(name=p.name, path=str(p))
        except Exception as ex:
            show_snack_bar(f"No se pudo abrir el selector: {ex}")
            return None
        finally:
            try:
                if root is not None:
                    root.destroy()
            except Exception:
                pass
    
    # ✅ Diálogo para pedir permiso de modificación
    def show_modification_dialog(selected_file):
        def confirm_modification(e):
            dialog.open = False
            page.update()
            # Navegar a la vista de Libro Diario (placeholder usando nombre de archivo como empresa)
            try:
                page.clean()
                page.add(book_journal_page(page, empresa=selected_file.name))
                page.update()
            except Exception as ex:
                show_snack_bar(f"No se pudo abrir el libro: {ex}")
        
        def cancel_modification(e):
            dialog.open = False
            page.update()
            show_snack_bar("Operación cancelada por el usuario")
        
        # Diálogo de confirmación
        dialog = ft.AlertDialog(
            title=ft.Text("Permiso para Modificar"),
            content=ft.Text(
                f"¿Deseas permitir que la aplicación modifique el archivo?\n\n"
                f"Archivo: {selected_file.name}\n\n"
                f"La aplicación podrá:\n"
                f"• Agregar nuevas columnas\n"
                f"• Modificar datos existentes\n"
                f"• Guardar cambios en el archivo original"
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cancel_modification),
                ft.TextButton("Permitir Modificación", on_click=confirm_modification),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    # ✅ Función para procesar la modificación (placeholder para tu lógica futura)
    def process_excel_modification(selected_file):
        # Reservado para importación futura desde Excel
        print(f"Archivo listo para importar/modificar: {selected_file.path}")
    
    # ✅ Función auxiliar para mostrar mensajes
    def show_snack_bar(message):
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            action="OK",
            duration=3000
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()
    
    # ✅ Función para abrir el explorador de archivos con Tkinter
    def open_file_explorer(_e=None):
        selected_file = pick_file_with_tk()
        if not selected_file:
            return
        print(f"Archivo seleccionado: {selected_file.name}")
        print(f"Ruta: {selected_file.path}")

        # Mostrar SnackBar de confirmación
        snack_bar = ft.SnackBar(
            content=ft.Text(f"Archivo seleccionado: {selected_file.name}"),
            action="OK",
            duration=3000
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

        # ✅ PEDIR PERMISO PARA MODIFICAR
        show_modification_dialog(selected_file)
    
    # Pasar la función a title_buttons
    buttons_content = title_buttons(open_file_explorer, page)
    
    # Contenido de la página
    fondo = create_modern_background(page)
    
    contenido = ft.Container(
        expand=True,
        padding=ft.padding.only(top=50, left=50, right=50, bottom=80),
        content=ft.Column(
            [
                # Fila superior (header)
                ft.Container(
                    content=ft.Row(
                        [
                            titlemenu(),
                            ft.Container(expand=True),
                            buttons_content,
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        expand=True,
                    ),
                ),
                title_viewfiles(page),
            ],
            expand=True,
        )
    )

    return ft.Stack(
        controls=[
            fondo,
            contenido
        ],
        expand=True
    )
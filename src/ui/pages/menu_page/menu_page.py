import flet as ft

from src.ui.components.backgrounds import create_modern_background
from src.ui.pages.menu_page.title_buttons import title_buttons
from src.ui.pages.menu_page.title_viewfiles import title_viewfiles
from src.ui.pages.menu_page.title_menu import titlemenu


def menu_page(page: ft.Page):
    # FilePicker se crea bajo demanda para evitar bloques visuales al abrir la app
    file_picker: ft.FilePicker | None = None

    # ✅ Función para manejar la selección de archivos
    def on_file_selected(e: ft.FilePickerResultEvent):
        if e.files:
            selected_file = e.files[0]
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
            
        else:
            print("No se seleccionó ningún archivo")
    
    # ✅ Diálogo para pedir permiso de modificación
    def show_modification_dialog(selected_file):
        def confirm_modification(e):
            dialog.open = False
            page.update()
            # ✅ Aquí irá tu lógica para modificar el Excel
            process_excel_modification(selected_file)
        
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
        show_snack_bar(f"✅ Permiso concedido para modificar: {selected_file.name}")
        
        # ✅ AQUÍ IRÁ TU LÓGICA PARA MODIFICAR EL EXCEL
        # Por ahora solo mostramos un mensaje
        print(f"PREPARADO para modificar: {selected_file.path}")
        
        # Futuramente aquí podrás:
        # 1. Leer el Excel con pandas
        # 2. Realizar modificaciones
        # 3. Guardar los cambios
        
        # Ejemplo futuro:
        # import pandas as pd
        # df = pd.read_excel(selected_file.path)
        # # ... tus modificaciones ...
        # df.to_excel(selected_file.path, index=False)
    
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
    
    # ✅ Asignar el evento de selección
    def ensure_file_picker():
        nonlocal file_picker
        if file_picker is None:
            file_picker = ft.FilePicker()
            file_picker.on_result = on_file_selected
            page.overlay.append(file_picker)
            page.update()
        return file_picker
    
    # ✅ Función para abrir el explorador de archivos
    async def open_file_explorer(e):
        picker = ensure_file_picker()
        await picker.pick_files(
            allowed_extensions=["xlsx", "xls"],
            dialog_title="Seleccionar libro contable Excel",
            file_type=ft.FilePickerFileType.CUSTOM,
            allow_multiple=False
        )
    
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
import flet as ft
import os
import tkinter as tk
from tkinter import filedialog

def main(page: ft.Page):
    page.title = "Diarium - Cargador de Archivos"

    def seleccionar_archivo_click(e):
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        ruta_seleccionada = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Excel", "*.xlsx"), ("CSV", "*.csv"), ("Todos", "*.*")]
        )
        root.destroy()

        if ruta_seleccionada:
            input_ruta.value = ruta_seleccionada
            log.value = f"✅ Archivo: {os.path.basename(ruta_seleccionada)}"
        else:
            log.value = "⚠️ Selección cancelada"
        page.update()

    # Si font_size y size fallan, creamos el texto y luego asignamos
    titulo = ft.Text("Importación de Datos")
    titulo.weight = "bold"
    # Intentamos asignar el tamaño de forma dinámica para ver cuál reconoce
    try:
        titulo.size = 25
    except:
        titulo.font_size = 25

    input_ruta = ft.TextField(
        label="Ruta del archivo",
        read_only=True,
        expand=True
    )

    log = ft.Text("")

    # Usamos Row y Column que son los más estables
    page.add(
        titulo,
        ft.Row([
            input_ruta,
            ft.Button(
                content="Explorar", 
                icon=ft.Icons.FOLDER_OPEN, 
                on_click=seleccionar_archivo_click
            )
        ]),
        log
    )

ft.run(main)
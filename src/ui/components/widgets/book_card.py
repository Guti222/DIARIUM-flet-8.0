import flet as ft
from typing import Optional, Callable
from data.models.libro import LibroDiario

def book_card(libro: LibroDiario, on_delete: Optional[Callable] = None) -> ft.Card:
    # Extraer sello de importación si viene concatenado en contador
    contador_val = libro.contador or ""
    sello_import = libro.fecha_importacion
    origen = getattr(libro, "origen", "creado") or "creado"

    info_column = [
        ft.Text(f"Empresa: {libro.nombre_empresa}", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
        ft.Text(f"Contador: {contador_val}", size=16, color=ft.Colors.BLACK),
        ft.Text(f"Año y mes: {libro.ano}/{libro.id_mes}", size=16, color=ft.Colors.BLACK),
    ]
    estado_texto = "Importado" if origen == "importado" else "Creado"
    estado_color = ft.Colors.GREY
    info_column.append(
        ft.Text(f"Estado: {estado_texto}", size=14, color=estado_color)
    )
    if sello_import:
        info_column.append(
            ft.Text(f"Importado: {sello_import}", size=14, color=ft.Colors.GREY, style=ft.TextStyle(italic=True))
        )

    return ft.Card(
        content=ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.BOOK, size=40, color=ft.Colors.BLUE),
                            ft.Container(width=10),
                            ft.Column(info_column),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.RED,
                        tooltip="Eliminar",
                        on_click=(lambda e: on_delete(e) if on_delete else None),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.BLUE_50,
            border=ft.border.all(1, ft.Colors.BLUE_200),
            border_radius=10,
            padding=ft.padding.all(5)
        ),
            margin=10,
            elevation=5,
    )
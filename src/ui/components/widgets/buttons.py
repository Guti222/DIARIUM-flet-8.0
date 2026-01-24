import flet as ft

def create_image_button(text: str, icon: str, on_click, description: str = ""):
    """
    Botón grande con ícono, perfecto para acciones principales
    """
    return ft.Container(
        content=ft.Column([
            ft.Icon(icon, size=20, color=ft.Colors.BLUE_700),
            ft.Text(text, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=ft.Colors.BLACK, size=12),
            ft.Text(description, size=10, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
        on_click=on_click,
        width=170,
        height=100,
        bgcolor=ft.Colors.BLUE_50,
        border_radius=15,
        padding=10,
        # alignment centrado: omitido temporalmente por cambios de API en Flet 0.80+
        # Efectos hover
        ink=True,
        border=ft.border.all(2, ft.Colors.BLUE_100),
    )
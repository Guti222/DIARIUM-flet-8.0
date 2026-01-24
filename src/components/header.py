"""
Header Component for DIARIUM
"""
import flet as ft


def create_header(title: str = "DIARIUM", show_back: bool = False, on_back=None) -> ft.Container:
    """Create a reusable header component
    
    Args:
        title: The title to display
        show_back: Whether to show back button
        on_back: Callback function for back button
        
    Returns:
        Header container control
    """
    controls = []
    
    if show_back and on_back:
        controls.append(
            ft.IconButton(
                icon=ft.icons.ARROW_BACK,
                on_click=on_back,
            )
        )
    
    controls.extend([
        ft.Icon(ft.icons.BOOK, size=30, color=ft.colors.BLUE),
        ft.Text(
            title,
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLUE,
        ),
    ])
    
    return ft.Container(
        content=ft.Row(
            controls=controls,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=20,
        bgcolor=ft.colors.BLUE_50,
    )

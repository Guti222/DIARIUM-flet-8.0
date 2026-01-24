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
                icon=(
                    getattr(ft.icons, "ARROW_BACK", getattr(ft.icons, "ARROW_LEFT", getattr(ft.icons, "CHEVRON_LEFT", None)))
                ),
                on_click=on_back,
            )
        )
    
    def _pick_icon(*names):
        for n in names:
            if hasattr(ft.icons, n):
                return getattr(ft.icons, n)
        for generic in ("MENU", "INFO", "HELP"):
            if hasattr(ft.icons, generic):
                return getattr(ft.icons, generic)
        return None

    controls.extend([
        ft.Icon(_pick_icon("BOOK", "MENU_BOOK", "LIBRARY_BOOKS", "DESCRIPTION"), size=30, color=ft.Colors.BLUE),
        ft.Text(
            title,
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE,
        ),
    ])
    
    return ft.Container(
        content=ft.Row(
            controls=controls,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=20,
        bgcolor=ft.Colors.BLUE_50,
    )

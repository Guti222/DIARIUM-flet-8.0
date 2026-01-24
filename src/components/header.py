"""
Header Component for DIARIUM
"""
import flet as ft


class Header(ft.UserControl):
    """Reusable header component"""
    
    def __init__(self, title: str = "DIARIUM", show_back: bool = False):
        """Initialize header
        
        Args:
            title: The title to display
            show_back: Whether to show back button
        """
        super().__init__()
        self.title_text = title
        self.show_back = show_back
        
    def build(self):
        """Build the header component"""
        controls = []
        
        if self.show_back:
            controls.append(
                ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=self._on_back,
                )
            )
        
        controls.extend([
            ft.Icon(ft.icons.BOOK, size=30, color=ft.colors.BLUE),
            ft.Text(
                self.title_text,
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
    
    def _on_back(self, e):
        """Handle back button click"""
        # Navigation will be handled by the router
        pass

"""
Home View for DIARIUM
"""
import flet as ft


class HomeView:
    """Home view of the diary application"""
    
    def __init__(self, page: ft.Page):
        """Initialize home view
        
        Args:
            page: The Flet page object
        """
        self.page = page
        
    def build(self) -> ft.Control:
        """Build and return the home view
        
        Returns:
            The home view control
        """
        # Header
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.icons.BOOK, size=40, color=ft.colors.BLUE),
                    ft.Text(
                        "DIARIUM",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=20,
            bgcolor=ft.colors.BLUE_50,
        )
        
        # Welcome message
        welcome = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Welcome to Your Personal Diary",
                        size=24,
                        weight=ft.FontWeight.W_500,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Start writing your thoughts and memories",
                        size=16,
                        color=ft.colors.GREY_700,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=40,
        )
        
        # Action buttons
        action_buttons = ft.Container(
            content=ft.Row(
                controls=[
                    ft.ElevatedButton(
                        "New Entry",
                        icon=ft.icons.ADD,
                        on_click=self._on_new_entry,
                        style=ft.ButtonStyle(
                            padding=ft.padding.all(20),
                        ),
                    ),
                    ft.OutlinedButton(
                        "View Entries",
                        icon=ft.icons.LIST,
                        on_click=self._on_view_entries,
                        style=ft.ButtonStyle(
                            padding=ft.padding.all(20),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            padding=20,
        )
        
        # Main layout
        return ft.Column(
            controls=[
                header,
                welcome,
                action_buttons,
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.START,
        )
    
    def _on_new_entry(self, e):
        """Handle new entry button click"""
        # TODO: Implement new entry functionality
        self.page.show_snack_bar(
            ft.SnackBar(content=ft.Text("New entry feature coming soon!"))
        )
    
    def _on_view_entries(self, e):
        """Handle view entries button click"""
        # TODO: Implement view entries functionality
        self.page.show_snack_bar(
            ft.SnackBar(content=ft.Text("View entries feature coming soon!"))
        )

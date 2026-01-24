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
        def _pick_icon(*names):
            for n in names:
                if hasattr(ft.icons, n):
                    return getattr(ft.icons, n)
            # generic fallbacks
            for generic in ("MENU", "INFO", "HELP"):
                if hasattr(ft.icons, generic):
                    return getattr(ft.icons, generic)
            return None

        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(_pick_icon("BOOK", "MENU_BOOK", "LIBRARY_BOOKS", "DESCRIPTION"), size=40, color=ft.Colors.BLUE),
                    ft.Text(
                        "DIARIUM",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=20,
            bgcolor=ft.Colors.BLUE_50,
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
                        color=ft.Colors.GREY_700,
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
                        icon=_pick_icon("ADD", "ADD_CIRCLE", "ADD_BOX", "PLUS_ONE"),
                        on_click=self._on_new_entry,
                        style=ft.ButtonStyle(
                            padding=ft.padding.all(20),
                        ),
                    ),
                    ft.OutlinedButton(
                        "View Entries",
                        icon=_pick_icon("LIST", "LIST_ALT", "FORMAT_LIST_BULLETED", "VIEW_LIST"),
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
        snack = ft.SnackBar(content=ft.Text("New entry feature coming soon!"))
        self.page.snack_bar = snack
        self.page.snack_bar.open = True
        self.page.update()
    
    def _on_view_entries(self, e):
        """Handle view entries button click"""
        # TODO: Implement view entries functionality
        snack = ft.SnackBar(content=ft.Text("View entries feature coming soon!"))
        self.page.snack_bar = snack
        self.page.snack_bar.open = True
        self.page.update()

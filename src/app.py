"""
Main Application Class for DIARIUM
"""
import flet as ft
from src.views.home_view import HomeView
from src.utils.config import AppConfig


class DiaryApp:
    """Main Diary Application class"""
    
    def __init__(self, page: ft.Page):
        """Initialize the application
        
        Args:
            page: The Flet page object
        """
        self.page = page
        self.config = AppConfig()
        self._setup_page()
        
    def _setup_page(self):
        """Setup page properties"""
        self.page.title = "DIARIUM - Your Personal Diary"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_min_width = 800
        self.page.window_min_height = 600
        
    def initialize(self):
        """Initialize and show the main view"""
        home_view = HomeView(self.page)
        self.page.add(home_view.build())
        self.page.update()

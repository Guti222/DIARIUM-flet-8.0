"""
DIARIUM - Diary Application with Flet 8.0
Main entry point for the application
"""
import flet as ft
from src.app import DiaryApp


def main(page: ft.Page):
    """Main application entry point"""
    app = DiaryApp(page)
    app.initialize()


if __name__ == "__main__":
    ft.app(target=main)

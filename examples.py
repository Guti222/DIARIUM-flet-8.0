"""
Example usage for DIARIUM components and features
"""
import flet as ft
from src.components.header import create_header
from src.models.diary_entry import DiaryEntry
from src.utils.helpers import get_current_date


def example_header_usage():
    """Example of using the header component"""
    # Simple header
    header = create_header()
    
    # Header with custom title
    custom_header = create_header(title="My Diary")
    
    # Header with back button
    def on_back_click(e):
        print("Back button clicked")
    
    header_with_back = create_header(
        title="Entry Details",
        show_back=True,
        on_back=on_back_click
    )
    
    return [header, custom_header, header_with_back]


def example_model_usage():
    """Example of using the DiaryEntry model"""
    # Create a new diary entry
    entry = DiaryEntry(
        title="My First Entry",
        content="Today was a great day!",
        tags="personal, happy"
    )
    
    print(f"Entry: {entry.title}")
    print(f"Created at: {entry.created_at}")
    print(f"Tags: {entry.tags}")
    
    return entry


def example_utility_usage():
    """Example of using utility functions"""
    current_date = get_current_date()
    print(f"Today's date: {current_date}")
    
    return current_date


if __name__ == "__main__":
    print("=== DIARIUM Examples ===")
    print("\n1. Using utilities:")
    example_utility_usage()
    
    print("\n2. Using models:")
    example_model_usage()
    
    print("\n3. Header components created successfully")

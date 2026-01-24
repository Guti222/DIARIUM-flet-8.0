"""
Utility functions for DIARIUM
"""
from datetime import datetime


def format_date(date: datetime, format_str: str = "%Y-%m-%d") -> str:
    """Format a datetime object to string
    
    Args:
        date: The datetime object to format
        format_str: The format string
        
    Returns:
        Formatted date string
    """
    return date.strftime(format_str)


def get_current_date() -> str:
    """Get current date as formatted string
    
    Returns:
        Current date string
    """
    return format_date(datetime.now())


def get_current_datetime() -> str:
    """Get current datetime as formatted string
    
    Returns:
        Current datetime string
    """
    return format_date(datetime.now(), "%Y-%m-%d %H:%M:%S")

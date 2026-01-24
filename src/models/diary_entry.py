"""
Data models for DIARIUM
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DiaryEntry:
    """Represents a diary entry"""
    
    id: Optional[int] = None
    title: str = ""
    content: str = ""
    created_at: datetime = None
    updated_at: datetime = None
    tags: str = ""
    
    def __post_init__(self):
        """Set default values after initialization"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

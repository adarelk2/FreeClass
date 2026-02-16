from dataclasses import dataclass
from typing import Any, Dict, Optional, Union
from datetime import datetime

@dataclass
class ClassRoomCategory:
    id: int
    name: str
    description: Optional[str]
    color: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    def get(self, key: str, default=None):
        """Dict-like get method for compatibility"""
        return getattr(self, key, default)
    
    def __str__(self) -> str:
        return f"ClassRoomCategory(id={self.id}, name={self.name})"
    
    def __repr__(self) -> str:
        return self.__str__()

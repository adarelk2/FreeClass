from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, Union

@dataclass
class User:
    username: str
    role: str
    id: Any
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "role": self.role,
            "id": self.id,
        }
    
    def get(self, key: str, default=None):
        """Dict-like get method for compatibility"""
        return getattr(self, key, default)
    
    def __str__(self) -> str:
        return f"User(id={self.id}, username={self.username}, role={self.role})"
    
    def __repr__(self) -> str:
        return self.__str__()

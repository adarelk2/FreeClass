from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

@dataclass
class Building:
    id: int
    building_name: str
    floors: int
    color: str
    
    def to_dict(self) -> Dict[str, Union[int, str]]:
        return {
            "id": self.id,
            "building_name": self.building_name,
            "floors": self.floors,
            "color": self.color,
        }
    
    def get(self, key: str, default=None):
        """Dict-like get method for compatibility"""
        return getattr(self, key, default)
    
    def __str__(self) -> str:
        return f"Building(id={self.id}, building_name={self.building_name}, floors={self.floors}, color={self.color})"
    
    def __repr__(self) -> str:
        return self.__str__()

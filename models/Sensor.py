from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

@dataclass
class Sensor:
    id: int
    room_id: int
    private_key: str
    public_key: str
    
    def to_dict(self) -> Dict[str, Union[int, str]]:
        return {
            "id": self.id,
            "room_id": self.room_id,
            "private_key": self.private_key,
            "public_key": self.public_key,
        }
    
    def get(self, key: str, default=None):
        """Dict-like get method for compatibility"""
        return getattr(self, key, default)
    
    def __str__(self) -> str:
        return f"Sensor(id={self.id}, room_id={self.room_id}, private_key={self.private_key}, public_key={self.public_key})"
    
    def __repr__(self) -> str:
        return self.__str__()

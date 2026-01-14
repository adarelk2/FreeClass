from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, Union

@dataclass
class Room:
    id: int
    id_building: int
    floor: int
    class_number: int
    def to_dict(self) -> Dict[str, Union[int, None]]:
        return {
            "id": self.id,
            "id_building": self.id_building,
            "floor": self.floor,
            "class_number": self.class_number,
        }
    
    def __str__(self) -> str:
        return f"Room(id={self.id}, id_building={self.id_building}, floor={self.floor}, class_number={self.class_number})"
    
    def __repr__(self) -> str:
        return self.__str__()  
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from models.Room import Room


class ClassroomsRepository(ABC):
    TABLE = "classrooms"

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    def get_by_id(self, classroom_id: int) -> Optional[Room]:
        pass

    @abstractmethod
    def list_by_building(self, building_id: int) -> List[Room]:
        pass

    @abstractmethod
    def list_by_floor(self, building_id: int, floor: int) -> List[Room]:
        pass

    @abstractmethod
    def get_all(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_with_filter(
        self,
        where: Optional[Dict[str, Any]] = None,
        *,
        order_by: Optional[str] = None,
        limit: Optional[int] = 200,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def update_by_id(self, classroom_id: int, fields: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    def delete_room_by_id(self, classroom_id: int) -> int:
        pass

    @abstractmethod
    def delete_rooms_by_building_id(self, building_id: int) -> int:
        pass

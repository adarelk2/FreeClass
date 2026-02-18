from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from models.ClassroomMotionEvent import ClassroomMotionEvent


class ClassroomMotionEventsRepository(ABC):
    TABLE = "classroom_motion_events"

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    def get_by_id(self, event_id: int) -> Optional[ClassroomMotionEvent]:
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
    def delete_events_by_room_id(self, classroom_id: int) -> int:
        pass

    @abstractmethod
    def delete_events_by_building_id(self, building_id: int) -> int:
        pass

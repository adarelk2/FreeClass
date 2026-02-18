from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from models.Sensor import Sensor


class SensorsRepository(ABC):
    TABLE = "sensors"

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    def get_by_id(self, sensor_id: int) -> Optional[Sensor]:
        pass

    @abstractmethod
    def get_by_privateKey(self, private_key: str) -> Optional[Sensor]:
        pass

    @abstractmethod
    def list_by_room_id(self, room_id: int) -> List[Sensor]:
        pass

    @abstractmethod
    def list_all(self) -> List[Sensor]:
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
    def update_by_id(self, sensor_id: int, fields: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    def update_room_by_token(self, token: str, room_id: int) -> int:
        pass

    @abstractmethod
    def delete_by_id(self, sensor_id: int) -> int:
        pass

    @abstractmethod
    def delete_by_token(self, token: str) -> int:
        pass

    @abstractmethod
    def delete_sensor_by_room_id(self, classroom_id: int) -> int:
        pass

    @abstractmethod
    def delete_sensors_by_building_id(self, building_id: int) -> int:
        pass

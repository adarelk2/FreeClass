from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from core.db import DB
from models.Sensor import Sensor
from repositories.sensors_repository_interface import SensorsRepository


def _parse_order_by(order_by: Optional[str]) -> Tuple[Optional[str], bool]:
    if not order_by:
        return None, False
    ob = order_by.strip()
    if not ob:
        return None, False
    if ob.startswith("-"):
        return ob[1:].strip(), True
    parts = ob.split()
    if len(parts) >= 2 and parts[1].upper() in ("ASC", "DESC"):
        return parts[0], parts[1].upper() == "DESC"
    return ob, False


class SensorsRepositoryMock(SensorsRepository):
    def __init__(self, db: DB) -> None:
        self.db = db

    def create(self, data: Dict[str, Any]) -> int:
        if not data:
            raise ValueError("create() requires data")
        return int(self.db.insert(self.TABLE, data))

    def get_by_id(self, sensor_id: int) -> Optional[Sensor]:
        rows = self.db.select(self.TABLE, {"id": sensor_id}) or []
        if not rows:
            return None
        row = rows[0]
        return Sensor(row['id'], row['room_id'], row['private_key'], row['public_key'])

    def get_by_privateKey(self, private_key: str) -> Optional[Sensor]:
        if not private_key:
            raise ValueError("get_by_privateKey() requires private_key")
        rows = self.db.select(self.TABLE, {"private_key": private_key}) or []
        if not rows:
            return None
        row = rows[0]
        return Sensor(row['id'], row['room_id'], row['private_key'], row['public_key'])

    def list_by_room_id(self, room_id: int) -> List[Sensor]:
        rows = self.db.select(self.TABLE, {"room_id": room_id}) or []
        return [Sensor(row['id'], row['room_id'], row['private_key'], row['public_key']) for row in rows]

    def list_all(self) -> List[Sensor]:
        rows = self.db.select(self.TABLE, {}) or []
        return [Sensor(row['id'], row['room_id'], row['private_key'], row['public_key']) for row in rows]

    def get_all(self) -> List[Dict[str, Any]]:
        return self.db.select(self.TABLE, {}) or []

    def get_with_filter(
        self,
        where: Optional[Dict[str, Any]] = None,
        *,
        order_by: Optional[str] = None,
        limit: Optional[int] = 200,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        rows = self.db.select(self.TABLE, where or {}) or []
        col, is_desc = _parse_order_by(order_by)
        if col:
            rows = sorted(rows, key=lambda r: r.get(col), reverse=is_desc)
        if offset is not None:
            rows = rows[offset:]
        if limit is not None:
            rows = rows[:limit]
        return rows

    def update_by_id(self, sensor_id: int, fields: Dict[str, Any]) -> int:
        if not fields:
            raise ValueError("update_by_id() requires at least one field")
        if "public_key" in fields and not fields["public_key"]:
            raise ValueError("update_by_id() cannot set empty 'public_key'")
        return self.db.update(self.TABLE, data=fields, where={"id": sensor_id})

    def update_room_by_token(self, token: str, room_id: int) -> int:
        if not token:
            raise ValueError("update_room_by_token() requires token")
        return self.db.update(self.TABLE, data={"room_id": room_id}, where={"token": token})

    def delete_by_id(self, sensor_id: int) -> int:
        return self.db.delete(self.TABLE, {"id": sensor_id})

    def delete_by_token(self, token: str) -> int:
        if not token:
            raise ValueError("delete_by_token() requires token")
        return self.db.delete(self.TABLE, {"token": token})

    def delete_sensor_by_room_id(self, classroom_id: int) -> int:
        return self.db.delete(self.TABLE, {"room_id": classroom_id})

    def delete_sensors_by_building_id(self, building_id: int) -> int:
        rooms = self.db.select("classrooms", {"id_building": building_id}) or []
        deleted = 0
        for room in rooms:
            rid = room.get("id")
            if rid is None:
                continue
            deleted += int(self.db.delete(self.TABLE, {"room_id": rid}))
        return deleted

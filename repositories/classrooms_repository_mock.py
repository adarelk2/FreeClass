from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from core.db import DB
from models.Room import Room
from repositories.classrooms_repository_interface import ClassroomsRepository


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


class ClassroomsRepositoryMock(ClassroomsRepository):
    def __init__(self, db: DB) -> None:
        self.db = db

    def create(self, data: Dict[str, Any]) -> int:
        if not data:
            raise ValueError("create() requires data")
        return int(self.db.insert(self.TABLE, data))

    def get_by_id(self, classroom_id: int) -> Optional[Room]:
        if not isinstance(classroom_id, int):
            raise TypeError(f"classroom_id must be int, got {type(classroom_id).__name__}")
        rows = self.db.select(self.TABLE, {"id": classroom_id}) or []
        if not rows:
            return None
        row = rows[0]
        return Room(row['id'], row['id_building'], row['floor'], row['class_number'])

    def list_by_building(self, building_id: int) -> List[Room]:
        rows = self.db.select(self.TABLE, {"id_building": building_id}) or []
        return [Room(row['id'], row['id_building'], row['floor'], row['class_number']) for row in rows]

    def list_by_floor(self, building_id: int, floor: int) -> List[Room]:
        rows = self.db.select(self.TABLE, {"id_building": building_id, "floor": floor}) or []
        return [Room(row['id'], row['id_building'], row['floor'], row['class_number']) for row in rows]

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

    def update_by_id(self, classroom_id: int, fields: Dict[str, Any]) -> int:
        if not fields:
            raise ValueError("update_by_id() requires at least one field")
        return self.db.update(self.TABLE, data=fields, where={"id": classroom_id})

    def delete_room_by_id(self, classroom_id: int) -> int:
        return self.db.delete(self.TABLE, {"id": classroom_id})

    def delete_rooms_by_building_id(self, building_id: int) -> int:
        return self.db.delete(self.TABLE, {"id_building": building_id})

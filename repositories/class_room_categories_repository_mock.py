from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from core.db import DB
from models.ClassRoomCategory import ClassRoomCategory
from repositories.class_room_categories_repository_interface import ClassRoomCategoriesRepository


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


class ClassRoomCategoriesRepositoryMock(ClassRoomCategoriesRepository):
    def __init__(self, db: DB) -> None:
        self.db = db

    def create(self, data: Dict[str, Any]) -> int:
        if not data:
            raise ValueError("create() requires data")
        return int(self.db.insert(self.TABLE, data))

    def get_by_id(self, classroom_id: int) -> Optional[ClassRoomCategory]:
        rows = self.db.select(self.TABLE, {"id": classroom_id}) or []
        if not rows:
            return None
        row = rows[0]
        return ClassRoomCategory(
            row['id'],
            row['name'],
            row.get('description'),
            row.get('color'),
            row.get('created_at'),
            row.get('updated_at')
        )

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

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from core.db import DB
from models.ClassroomMotionEvent import ClassroomMotionEvent
from repositories.classroom_motion_events_repository_interface import ClassroomMotionEventsRepository


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


class ClassroomMotionEventsRepositoryMysql(ClassroomMotionEventsRepository):
    def __init__(self, db: DB) -> None:
        self.db = db

    def create(self, data: Dict[str, Any]) -> int:
        if not data:
            raise ValueError("create() requires data")

        new_id = self.db.insert(self.TABLE, data)
        if new_id is None:
            raise RuntimeError("Insert succeeded but no lastrowid was returned")
        return int(new_id)

    def get_by_id(self, event_id: int) -> Optional[ClassroomMotionEvent]:
        rows = self.db.query("SELECT * FROM classroom_motion_events WHERE id = %s", (event_id,))
        if rows:
            row = rows[0]
            return ClassroomMotionEvent(
                row['id'],
                row['classroom_id'],
                row['sensor_id'],
                row['event_time'],
                row['received_at'],
                row['event_type'],
                row['confidence'],
                row['payload']
            )
        return None

    def get_all(self) -> List[Dict[str, Any]]:
        return self.db.query("SELECT * FROM classroom_motion_events", ()) or []

    def get_with_filter(
        self,
        where: Optional[Dict[str, Any]] = None,
        *,
        order_by: Optional[str] = None,
        limit: Optional[int] = 200,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM classroom_motion_events"
        params: List[Any] = []

        if where:
            where_parts = []
            for col, value in where.items():
                where_parts.append(f"{col} = %s")
                params.append(value)
            query += " WHERE " + " AND ".join(where_parts)

        col, is_desc = _parse_order_by(order_by)
        if col:
            query += f" ORDER BY {col} {'DESC' if is_desc else 'ASC'}"

        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)

        if offset is not None:
            query += " OFFSET %s"
            params.append(offset)

        return self.db.query(query, tuple(params)) or []

    def delete_events_by_room_id(self, classroom_id: int) -> int:
        return self.db.delete(self.TABLE, {"classroom_id": classroom_id})

    def delete_events_by_building_id(self, building_id: int) -> int:
        query = """
            DELETE me FROM classroom_motion_events me
            INNER JOIN classrooms c ON me.classroom_id = c.id
            WHERE c.id_building = %s
        """
        return self.db.execute(query, (building_id,))

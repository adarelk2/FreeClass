# models/classroom_motion_events_model.py
from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.mysql import MySQL


class ClassroomMotionEventsModel:
    """
    classroom_motion_events table model בלבד.

    Table columns you described:
      - classroom_id (FK)
      - sensor_id
      - event_time
      - received_at
      - confidence
      - payload
    """

    TABLE = "classroom_motion_events"

    def __init__(self, db: MySQL) -> None:
        self.db = db

    # ----------------------------
    # CREATE
    # ----------------------------

    def create(self, data: Dict[str, Any]) -> int:
        """
        Insert a motion event row.
        Returns inserted id.
        """
        if not data:
            raise ValueError("create() requires data")

        new_id = self.db.insert(self.TABLE, data)
        if new_id is None:
            raise RuntimeError("Insert succeeded but no lastrowid was returned")
        return int(new_id)

    # ----------------------------
    # READ
    # ----------------------------

    def get_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        rows = self.db.select(self.TABLE, {"id": event_id})
        return rows[0] if rows else None

    def list_by_classroom(self, classroom_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Motion history for a classroom.
        Still events-only, no joins.
        """
        if limit <= 0:
            raise ValueError("limit must be > 0")

        query = f"""
        SELECT *
        FROM {self.TABLE}
        WHERE classroom_id = %s
        ORDER BY received_at DESC
        LIMIT %s
        """

        cursor = self.db.connection.cursor(dictionary=True)
        try:
            cursor.execute(query, (classroom_id, limit))
            return cursor.fetchall()
        finally:
            cursor.close()

    def list_latest(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Latest events across all classrooms.
        """
        if limit <= 0:
            raise ValueError("limit must be > 0")

        query = f"""
        SELECT *
        FROM {self.TABLE}
        ORDER BY received_at DESC
        LIMIT %s
        """

        cursor = self.db.connection.cursor(dictionary=True)
        try:
            cursor.execute(query, (limit,))
            return cursor.fetchall()
        finally:
            cursor.close()

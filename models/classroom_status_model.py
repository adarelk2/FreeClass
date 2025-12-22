# models/classroom_status_model.py
from __future__ import annotations

from typing import Any, Dict, Optional

from core.mysql import MySQL


class ClassroomStatusModel:
    """
    classroom_status table model בלבד.

    You said:
    - one row per classroom
    - updated via UPSERT on every motion event

    Assumption:
    - classroom_status has UNIQUE/PK on classroom_id
    - columns include at least:
        classroom_id, last_motion_time, last_sensor_id, last_confidence, payload/last_payload, updated_at
    Adjust column names below if yours differ.
    """

    TABLE = "classroom_status"

    def __init__(self, db: MySQL) -> None:
        self.db = db

    # ----------------------------
    # READ
    # ----------------------------

    def get_by_classroom_id(self, classroom_id: int) -> Optional[Dict[str, Any]]:
        rows = self.db.select(self.TABLE, {"classroom_id": classroom_id})
        return rows[0] if rows else None

    # ----------------------------
    # UPSERT (single-table)
    # ----------------------------

    def upsert(
        self,
        classroom_id: int,
        last_motion_time: Any,
        last_sensor_id: str,
        last_confidence: int,
        last_payload: Any,
    ) -> None:
        """
        Insert or update the single status row for a classroom.
        This stays inside classroom_status only.

        last_motion_time can be:
          - datetime
          - MySQL string timestamp
          - or you can pass "NOW(3)" via separate method (not recommended with params)
        """

        query = f"""
        INSERT INTO {self.TABLE}
          (classroom_id, last_motion_time, last_sensor_id, last_confidence, last_payload, updated_at)
        VALUES
          (%s, %s, %s, %s, %s, NOW(3))
        ON DUPLICATE KEY UPDATE
          last_motion_time = VALUES(last_motion_time),
          last_sensor_id   = VALUES(last_sensor_id),
          last_confidence  = VALUES(last_confidence),
          last_payload     = VALUES(last_payload),
          updated_at       = VALUES(updated_at)
        """

        cursor = self.db.connection.cursor()
        try:
            cursor.execute(
                query,
                (classroom_id, last_motion_time, last_sensor_id, last_confidence, last_payload),
            )
            self.db.connection.commit()
        finally:
            cursor.close()

    # ----------------------------
    # UPDATE (optional direct update)
    # ----------------------------

    def update_by_classroom_id(self, classroom_id: int, fields: Dict[str, Any]) -> int:
        """
        Simple update for the status row.
        Uses your MySQL.update (commits internally).
        """
        if not fields:
            raise ValueError("update_by_classroom_id() requires at least one field")

        return self.db.update(self.TABLE, filter=fields, where={"classroom_id": classroom_id})

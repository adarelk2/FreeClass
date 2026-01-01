# models/classroom_motion_events_model.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
from core.mysql import MySQL
from core.model_base import ModelBase

class ClassroomMotionEventsModel(ModelBase):
    """

+--------------+------------------+------+-----+----------------------+-------------------+
| Field        | Type             | Null | Key | Default              | Extra             |
+--------------+------------------+------+-----+----------------------+-------------------+
| id           | bigint unsigned  | NO   | PRI | NULL                 | auto_increment    |
| classroom_id | int              | NO   | MUL | NULL                 |                   |
| sensor_id    | varchar(64)      | NO   | MUL | NULL                 |                   |
| event_time   | datetime(3)      | NO   |     | CURRENT_TIMESTAMP(3) | DEFAULT_GENERATED |
| received_at  | datetime(3)      | NO   |     | CURRENT_TIMESTAMP(3) | DEFAULT_GENERATED |
| event_type   | varchar(32)      | NO   |     | motion               |                   |
| confidence   | tinyint unsigned | YES  |     | NULL                 |                   |
| payload      | json             | YES  |     | NULL                 |                   |
+--------------+------------------+------+-----+----------------------+-------------------+

    """

    def __init__(self, db: MySQL) -> None:
        super().__init__("classroom_motion_events")
        self.db = db

    def create(self, data: Dict[str, Any]) -> int:
        if not data:
            raise ValueError("create() requires data")

        new_id = self.db.insert(self.TABLE, data)
        if new_id is None:
            raise RuntimeError("Insert succeeded but no lastrowid was returned")
        return int(new_id)

    def get_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        rows = self.db.select(self.TABLE, {"id": event_id})
        return rows[0] if rows else None

    def delete_events_by_room_id(self, classroom_id):
        return self.db.delete(self.TABLE,{"classroom_id": classroom_id})
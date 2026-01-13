# models/sensors_model.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
from core.infrastructure.mysql import MySQL
from core.model_base import ModelBase

class SensorsModel(ModelBase):
    """
    Sensors table model בלבד.

    Expected schema:

    +---------+--------------+------+-----+---------+----------------+
    | Field   | Type         | Null | Key | Default | Extra          |
    +---------+--------------+------+-----+---------+----------------+
    | id      | int unsigned | NO   | PRI | NULL    | auto_increment |
    | room_id | int          | NO   | MUL | NULL    |                |
    | private_key   | varchar(255) | NO   | UNI | NULL    |                |
    | public_key   | varchar(255) | NO   | UNI | NULL    |                |
    +---------+--------------+------+-----+---------+----------------+

    Notes:
    - token should be UNIQUE (recommended).
    - room_id should reference classrooms(id).
    """

    def __init__(self, db: MySQL) -> None:
        super().__init__("sensors")
        self.db = db

    # ---------- Create ----------
    def create(self, data: Dict[str, Any]) -> int:
        if not data:
            raise ValueError("create() requires data")
       
        new_id = self.db.insert(self.TABLE, data)
        if new_id is None:
            raise RuntimeError("Insert succeeded but no lastrowid was returned")
        return int(new_id)

    # ---------- Read ----------
    def get_by_id(self, sensor_id: int) -> Optional[Dict[str, Any]]:
        rows = self.db.select(self.TABLE, {"id": sensor_id})
        return rows[0] if rows else None

    def get_by_privateKey(self, private_key: str) -> Optional[Dict[str, Any]]:
        if not private_key:
            raise ValueError("get_by_privateKey() requires private_key")
        rows = self.db.select(self.TABLE, {"private_key": private_key})
        return rows[0] if rows else None

    def list_by_room_id(self, room_id: int) -> List[Dict[str, Any]]:
        return self.db.select(self.TABLE, {"room_id": room_id}) or []

    def list_all(self) -> List[Dict[str, Any]]:
        return self.db.select(self.TABLE, {}) or []

    # ---------- Update ----------
    def update_by_id(self, sensor_id: int, fields: Dict[str, Any]) -> int:
        if not fields:
            raise ValueError("update_by_id() requires at least one field")

        # Optional: prevent empty token updates
        if "public_key" in fields and not fields["public_key"]:
            raise ValueError("update_by_id() cannot set empty 'public_key'")

        return self.db.update(self.TABLE, filter=fields, where={"id": sensor_id})

    def update_room_by_token(self, token: str, room_id: int) -> int:
        if not token:
            raise ValueError("update_room_by_token() requires token")
        return self.db.update(self.TABLE, filter={"room_id": room_id}, where={"token": token})

    # ---------- Delete ----------
    def delete_by_id(self, sensor_id: int) -> int:
        return self.db.delete(self.TABLE, {"id": sensor_id})

    def delete_by_token(self, token: str) -> int:
        if not token:
            raise ValueError("delete_by_token() requires token")
        return self.db.delete(self.TABLE, {"token": token})

    def delete_sensor_by_room_id(self, classroom_id):
        return self.db.delete(self.TABLE,{"room_id": classroom_id})
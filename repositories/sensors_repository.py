# repositories/sensors_repository.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
from core.infrastructure.mysql import MySQL
from core.model_base import ModelBase
from models.Sensor import Sensor

class SensorsRepository(ModelBase):
    """
    Sensors table repository.

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
    def get_by_id(self, sensor_id: int) -> Optional[Sensor]:
        rows = self.db.select(self.TABLE, {"id": sensor_id})
        if rows:
            row = rows[0]
            return Sensor(row['id'], row['room_id'], row['private_key'], row['public_key'])
        return None

    def get_by_privateKey(self, private_key: str) -> Optional[Sensor]:
        if not private_key:
            raise ValueError("get_by_privateKey() requires private_key")
        rows = self.db.select(self.TABLE, {"private_key": private_key})
        if rows:
            row = rows[0]
            return Sensor(row['id'], row['room_id'], row['private_key'], row['public_key'])
        return None

    def list_by_room_id(self, room_id: int) -> List[Sensor]:
        rows = self.db.select(self.TABLE, {"room_id": room_id}) or []
        return [Sensor(row['id'], row['room_id'], row['private_key'], row['public_key']) for row in rows]

    def list_all(self) -> List[Sensor]:
        rows = self.db.select(self.TABLE, {}) or []
        return [Sensor(row['id'], row['room_id'], row['private_key'], row['public_key']) for row in rows]

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

    def delete_sensors_by_building_id(self, building_id: int):
        """
        Delete all sensors for rooms in a building (single query via INNER JOIN).
        Returns number of rows deleted.
        """
        query = """
            DELETE s FROM sensors s
            INNER JOIN classrooms c ON s.room_id = c.id
            WHERE c.id_building = %s
        """
        return self.db.execute(query, (building_id,))

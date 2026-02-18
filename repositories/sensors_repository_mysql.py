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


class SensorsRepositoryMysql(SensorsRepository):
    def __init__(self, db: DB) -> None:
        self.db = db

    def create(self, data: Dict[str, Any]) -> int:
        if not data:
            raise ValueError("create() requires data")

        new_id = self.db.insert(self.TABLE, data)
        if new_id is None:
            raise RuntimeError("Insert succeeded but no lastrowid was returned")
        return int(new_id)

    def get_by_id(self, sensor_id: int) -> Optional[Sensor]:
        rows = self.db.query("SELECT * FROM sensors WHERE id = %s", (sensor_id,))
        if rows:
            row = rows[0]
            return Sensor(row['id'], row['room_id'], row['private_key'], row['public_key'])
        return None

    def get_by_privateKey(self, private_key: str) -> Optional[Sensor]:
        if not private_key:
            raise ValueError("get_by_privateKey() requires private_key")
        rows = self.db.query("SELECT * FROM sensors WHERE private_key = %s", (private_key,))
        if rows:
            row = rows[0]
            return Sensor(row['id'], row['room_id'], row['private_key'], row['public_key'])
        return None

    def list_by_room_id(self, room_id: int) -> List[Sensor]:
        rows = self.db.query("SELECT * FROM sensors WHERE room_id = %s", (room_id,)) or []
        return [Sensor(row['id'], row['room_id'], row['private_key'], row['public_key']) for row in rows]

    def list_all(self) -> List[Sensor]:
        rows = self.db.query("SELECT * FROM sensors", ()) or []
        return [Sensor(row['id'], row['room_id'], row['private_key'], row['public_key']) for row in rows]

    def get_all(self) -> List[Dict[str, Any]]:
        return self.db.query("SELECT * FROM sensors", ()) or []

    def get_with_filter(
        self,
        where: Optional[Dict[str, Any]] = None,
        *,
        order_by: Optional[str] = None,
        limit: Optional[int] = 200,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM sensors"
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
        query = """
            DELETE s FROM sensors s
            INNER JOIN classrooms c ON s.room_id = c.id
            WHERE c.id_building = %s
        """
        return self.db.execute(query, (building_id,))

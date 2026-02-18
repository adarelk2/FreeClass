# repositories/classrooms_repository.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
from core.infrastructure.mysql import MySQL
from core.model_base import ModelBase
from models.Room import Room

class ClassroomsRepository(ModelBase):
    """
   
+--------------+--------------+------+-----+---------+----------------+
| Field        | Type         | Null | Key | Default | Extra          |
+--------------+--------------+------+-----+---------+----------------+
| id           | int          | NO   | PRI | NULL    | auto_increment |
| id_building  | int unsigned | NO   | MUL | NULL    |                |
| floor        | int          | NO   |     | NULL    |                |
| class_number | int          | NO   |     | NULL    |                |
+--------------+--------------+------+-----+---------+----------------+

    """

    def __init__(self, db: MySQL) -> None:
        super().__init__("classrooms")
        self.db = db

    def create(self, data: Dict[str, Any]) -> int:
        if not data:
            raise ValueError("create() requires data")

        new_id = self.db.insert(self.TABLE, data)
        if new_id is None:
            raise RuntimeError("Insert succeeded but no lastrowid was returned")
        return int(new_id)


    def get_by_id(self, classroom_id: int) -> Room:
        if not isinstance(classroom_id, int):
            raise TypeError(f"classroom_id must be int, got {type(classroom_id).__name__}")
        
        rows = self.db.query("SELECT * FROM classrooms WHERE id = %s", (classroom_id,))
        return Room(rows[0]['id'], rows[0]['id_building'], rows[0]['floor'], rows[0]['class_number']) if rows else None


    def list_by_building(self, building_id: int) -> List[Room]:
        rows = self.db.query("SELECT * FROM classrooms WHERE id_building = %s", (building_id,))
        return [Room(row['id'], row['id_building'], row['floor'], row['class_number']) for row in rows]

    def list_by_floor(self, building_id: int, floor: int) -> List[Room]:
        rows = self.db.query(
            "SELECT * FROM classrooms WHERE id_building = %s AND floor = %s",
            (building_id, floor),
        )
        return [Room(row['id'], row['id_building'], row['floor'], row['class_number']) for row in rows]

    def update_by_id(self, classroom_id: int, fields: Dict[str, Any]) -> int:
        if not fields:
            raise ValueError("update_by_id() requires at least one field")

        return self.db.update(
            self.TABLE,
            data=fields,
            where={"id": classroom_id},
        )



    def delete_room_by_id(self, classroom_id: int) -> int:
        """Delete room without cascade. Returns number of rows deleted."""
        return self.db.delete(self.TABLE,{"id": classroom_id})

    def delete_rooms_by_building_id(self, building_id: int) -> int:
        """Delete all rooms in a building (single query). Returns number of rows deleted."""
        return self.db.delete(self.TABLE, {"id_building": building_id})

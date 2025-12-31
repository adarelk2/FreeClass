# models/classrooms_model.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
from core.mysql import MySQL
from core.model_base import ModelBase

class ClassRoomsModel(ModelBase):
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


    def get_by_id(self, classroom_id: int) -> Optional[Dict[str, Any]]:
        rows = self.db.select(self.TABLE, {"id": classroom_id})
        return rows[0] if rows else None


    def list_by_building(self, building_id: int) -> List[Dict[str, Any]]:
        return self.db.select(self.TABLE, {"id_building": building_id})

    def list_by_floor(self, building_id: int, floor: int) -> List[Dict[str, Any]]:
        return self.db.select(
            self.TABLE,
            {
                "id_building": building_id,
                "floor": floor,
            },
        )


    def update_by_id(self, classroom_id: int, fields: Dict[str, Any]) -> int:
        if not fields:
            raise ValueError("update_by_id() requires at least one field")

        return self.db.update(
            self.TABLE,
            filter=fields,
            where={"id": classroom_id},
        )



    def delete_room_by_id(self, classroom_id):
        return self.db.delete(self.TABLE,{"id": classroom_id})



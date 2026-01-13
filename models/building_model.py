# models/building_model.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
from core.infrastructure.mysql import MySQL
from core.model_base import ModelBase

class BuildingModel(ModelBase):
    """
    Buildings table model בלבד.
   

+---------------+--------------+------+-----+---------+----------------+
| Field         | Type         | Null | Key | Default | Extra          |
+---------------+--------------+------+-----+---------+----------------+
| id            | int unsigned | NO   | PRI | NULL    | auto_increment |
| building_name | varchar(255) | NO   |     | NULL    |                |
| floors        | int          | NO   |     | NULL    |                |
| color         | varchar(16)  | NO   |     | #000    |                |
+---------------+--------------+------+-----+---------+----------------+


    """

    def __init__(self, db: MySQL) -> None:
        super().__init__("buildings")
        self.db = db

    def create(self, data: Dict[str, Any]) -> int:
        if not data:
            raise ValueError("create() requires data")

        new_id = self.db.insert(self.TABLE, data)
        if new_id is None:
            raise RuntimeError("Insert succeeded but no lastrowid was returned")
        return int(new_id)


    def get_by_id(self, building_id: int) -> Optional[Dict[str, Any]]:
        rows = self.db.select(self.TABLE, {"id": building_id})
        return rows[0] if rows else None


    def update_by_id(self, building_id: int, fields: Dict[str, Any]) -> int:
        if not fields:
            raise ValueError("update_by_id() requires at least one field")
        return self.db.update(self.TABLE, filter=fields, where={"id": building_id})

    def delete_build_by_id(self, building_id):
        return self.db.delete(self.TABLE, {"id": building_id})
# repositories/building_repository.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
from core.infrastructure.mysql import MySQL
from core.model_base import ModelBase
from models.Building import Building

class BuildingRepository(ModelBase):
    """
    Buildings table repository.
   

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


    def get_by_id(self, building_id: int) -> Optional[Building]:
        rows = self.db.query("SELECT * FROM buildings WHERE id = %s", (building_id,))
        if rows:
            row = rows[0]
            return Building(row['id'], row['building_name'], row['floors'], row['color'])
        return None


    def update_by_id(self, building_id: int, fields: Dict[str, Any]) -> int:
        if not fields:
            raise ValueError("update_by_id() requires at least one field")
        return self.db.update(self.TABLE, data=fields, where={"id": building_id})

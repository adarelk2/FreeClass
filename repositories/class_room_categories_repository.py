# repositories/class_room_categories_repository.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
from core.infrastructure.mysql import MySQL
from core.model_base import ModelBase
from models.ClassRoomCategory import ClassRoomCategory

class ClassRoomCategoriesRepository(ModelBase):
    """
   
+-------------+--------------+------+-----+-------------------+-----------------------------+
| Field       | Type         | Null | Key | Default           | Extra                       |
+-------------+--------------+------+-----+-------------------+-----------------------------+
| id          | int unsigned | NO   | PRI | NULL              | auto_increment              |
| name        | varchar(64)  | NO   | UNI | NULL              |                             |
| description | varchar(255) | YES  |     | NULL              |                             |
| color       | varchar(16)  | NO   |     | #6c757d           |                             |
| created_at  | datetime     | NO   |     | CURRENT_TIMESTAMP | DEFAULT_GENERATED           |
| updated_at  | datetime     | YES  |     | NULL              | on update CURRENT_TIMESTAMP |
+-------------+--------------+------+-----+-------------------+-----------------------------+

    """

    def __init__(self, db: MySQL) -> None:
        super().__init__("classroom_categories")
        self.db = db


    def create(self, data: Dict[str, Any]) -> int:
        if not data:
            raise ValueError("create() requires data")

        new_id = self.db.insert(self.TABLE, data)
        if new_id is None:
            raise RuntimeError("Insert succeeded but no lastrowid was returned")
        return int(new_id)


    def get_by_id(self, classroom_id: int) -> Optional[ClassRoomCategory]:
        rows = self.db.query("SELECT * FROM classroom_categories WHERE id = %s", (classroom_id,))
        if rows:
            row = rows[0]
            return ClassRoomCategory(
                row['id'],
                row['name'],
                row['description'],
                row['color'],
                row['created_at'],
                row['updated_at']
            )
        return None

# models/classrooms_model.py
from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.mysql import MySQL


class ClassRoomsModel:
    """
    Classrooms table model בלבד.
    טבלה: classrooms (id, id_building, floor, class_number)

    No joins. No status logic. No dashboard queries.
    """

    TABLE = "classrooms"

    def __init__(self, db: MySQL) -> None:
        self.db = db

    # ----------------------------
    # CREATE
    # ----------------------------

    def create(self, data: Dict[str, Any]) -> int:
        """
        Insert a new classroom.

        Expected fields:
          - id_building
          - floor
          - class_number

        Returns:
          inserted id
        """
        if not data:
            raise ValueError("create() requires data")

        new_id = self.db.insert(self.TABLE, data)
        if new_id is None:
            raise RuntimeError("Insert succeeded but no lastrowid was returned")
        return int(new_id)

    # ----------------------------
    # READ
    # ----------------------------

    def get_by_id(self, classroom_id: int) -> Optional[Dict[str, Any]]:
        rows = self.db.select(self.TABLE, {"id": classroom_id})
        return rows[0] if rows else None

    def list_all(self) -> List[Dict[str, Any]]:
        cursor = self.db.connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM {self.TABLE} ORDER BY id ASC")
            return cursor.fetchall()
        finally:
            cursor.close()

    def list_by_building(self, building_id: int) -> List[Dict[str, Any]]:
        """
        List classrooms for a given building.
        Still classrooms-only (no joins).
        """
        return self.db.select(self.TABLE, {"id_building": building_id})

    def list_by_floor(self, building_id: int, floor: int) -> List[Dict[str, Any]]:
        return self.db.select(
            self.TABLE,
            {
                "id_building": building_id,
                "floor": floor,
            },
        )

    def exists(self, classroom_id: int) -> bool:
        cursor = self.db.connection.cursor()
        try:
            cursor.execute(
                f"SELECT 1 FROM {self.TABLE} WHERE id = %s LIMIT 1",
                (classroom_id,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()

    # ----------------------------
    # UPDATE
    # ----------------------------

    def update_by_id(self, classroom_id: int, fields: Dict[str, Any]) -> int:
        """
        Update classroom by id.

        Returns:
          affected rows
        """
        if not fields:
            raise ValueError("update_by_id() requires at least one field")

        return self.db.update(
            self.TABLE,
            filter=fields,
            where={"id": classroom_id},
        )

    # ----------------------------
    # DELETE (optional)
    # ----------------------------

    def delete_by_id(self, classroom_id: int) -> int:
        cursor = self.db.connection.cursor()
        try:
            cursor.execute(
                f"DELETE FROM {self.TABLE} WHERE id = %s",
                (classroom_id,),
            )
            self.db.connection.commit()
            return cursor.rowcount
        finally:
            cursor.close()

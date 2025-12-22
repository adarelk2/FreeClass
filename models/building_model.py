# models/building_model.py
from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.mysql import MySQL


class BuildingModel:
    """
    Buildings table model בלבד.
    טבלה: buildings (id, building_name, floors, ...)

    No joins. No dashboard logic. No cross-table queries.
    """

    TABLE = "buildings"

    def __init__(self, db: MySQL) -> None:
        self.db = db

    # ----------------------------
    # CREATE
    # ----------------------------

    def create(self, data: Dict[str, Any]) -> int:
        """
        Insert a new building.

        Expected minimal fields:
          - building_name
          - floors
        But we allow any extra columns you have in buildings.

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

    def get_by_id(self, building_id: int) -> Optional[Dict[str, Any]]:
        rows = self.db.select(self.TABLE, {"id": building_id})
        return rows[0] if rows else None

    def list_all(self) -> List[Dict[str, Any]]:
        """
        List all buildings.
        This is still 'buildings only' and does not join or aggregate.
        """
        cursor = self.db.connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM {self.TABLE} ORDER BY id ASC")
            return cursor.fetchall()
        finally:
            cursor.close()

    def exists(self, building_id: int) -> bool:
        cursor = self.db.connection.cursor()
        try:
            cursor.execute(f"SELECT 1 FROM {self.TABLE} WHERE id = %s LIMIT 1", (building_id,))
            return cursor.fetchone() is not None
        finally:
            cursor.close()

    # ----------------------------
    # UPDATE
    # ----------------------------

    def update_by_id(self, building_id: int, fields: Dict[str, Any]) -> int:
        """
        Update building by id.

        Returns:
          affected rows
        """
        if not fields:
            raise ValueError("update_by_id() requires at least one field")
        return self.db.update(self.TABLE, filter=fields, where={"id": building_id})

    # ----------------------------
    # DELETE (optional)
    # ----------------------------

    def delete_by_id(self, building_id: int) -> int:
        """
        Delete building by id.

        NOTE: Your current MySQL wrapper doesn't have delete().
        We implement it here as raw SQL, still buildings-only.
        Returns affected rows.
        """
        cursor = self.db.connection.cursor()
        try:
            cursor.execute(f"DELETE FROM {self.TABLE} WHERE id = %s", (building_id,))
            self.db.connection.commit()
            return cursor.rowcount
        finally:
            cursor.close()

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from core.db import DB
from models.Building import Building
from repositories.building_repository_interface import BuildingRepository


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


class BuildingRepositoryMysql(BuildingRepository):
    def __init__(self, db: DB) -> None:
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

    def get_all(self) -> List[Dict[str, Any]]:
        return self.db.query("SELECT * FROM buildings", ()) or []

    def get_with_filter(
        self,
        where: Optional[Dict[str, Any]] = None,
        *,
        order_by: Optional[str] = None,
        limit: Optional[int] = 200,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM buildings"
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

    def update_by_id(self, building_id: int, fields: Dict[str, Any]) -> int:
        if not fields:
            raise ValueError("update_by_id() requires at least one field")
        return self.db.update(self.TABLE, data=fields, where={"id": building_id})

    def delete_building_by_id(self, building_id: int) -> int:
        return self.db.delete(self.TABLE, {"id": building_id})

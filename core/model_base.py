# core/model_base.py
from __future__ import annotations
from typing import Any, Dict, List, Optional


class ModelBase:
    def __init__(self, _tbname) -> None:
        self.TABLE = _tbname

    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all rows from the table using query().
        """
        return self.db.query(f"SELECT * FROM {self.TABLE}", ())

    def get_with_filter(
        self,
        where: Optional[Dict[str, Any]] = None,
        *,
        order_by: Optional[str] = None,
        limit: Optional[int] = 200,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get rows with filter using query().
        - where: dict of column=value conditions ANDed together
        - order_by: "column" (ASC) or "-column" (DESC)
        - limit/offset: pagination
        """
        if not where:
            # No filters, use get_all()
            query = f"SELECT * FROM {self.TABLE}"
            params = []
        else:
            # Build WHERE clause
            where_parts = []
            params = []
            for col, val in where.items():
                where_parts.append(f"{col} = %s")
                params.append(val)
            where_clause = " AND ".join(where_parts)
            query = f"SELECT * FROM {self.TABLE} WHERE {where_clause}"

        # Add ORDER BY
        if order_by:
            ob = order_by.strip()
            if ob.startswith("-"):
                col = ob[1:].strip()
                query += f" ORDER BY {col} DESC"
            else:
                parts = ob.split()
                if len(parts) >= 2 and parts[1].upper() in ("ASC", "DESC"):
                    col = parts[0]
                    direction = parts[1].upper()
                else:
                    col = ob
                    direction = "ASC"
                query += f" ORDER BY {col} {direction}"

        # Add LIMIT/OFFSET
        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)
        if offset is not None:
            query += " OFFSET %s"
            params.append(offset)

        return self.db.query(query, tuple(params))


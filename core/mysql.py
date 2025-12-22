# core/mysql.py
from __future__ import annotations

from typing import Optional, Any, Dict, List, Tuple

import re
import mysql.connector
from mysql.connector import MySQLConnection


class MySQL:
    """
    Minimal MySQL wrapper with:
    - insert/update/delete
    - select with ADT-style filters + safe-ish order_by + limit/offset
    """

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        port: int = 3306,
        ssl_required: bool = True,
    ) -> None:
        self.connection: MySQLConnection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            ssl_disabled=(not ssl_required),
        )

        self.connection.autocommit = True

    # ---------------------------------
    # INTERNAL HELPERS
    # ---------------------------------

    def _build_where(self, filters: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """
        Builds: " WHERE a=%s AND b=%s" and values list
        Equality AND only.
        """
        if not filters:
            return "", []

        parts: List[str] = []
        values: List[Any] = []
        for k, v in filters.items():
            # allow only simple identifier chars for column names
            if not str(k).replace("_", "").isalnum():
                raise ValueError("filter key contains invalid characters")
            parts.append(f"{k}=%s")
            values.append(v)

        return " WHERE " + " AND ".join(parts), values

    def _build_order_limit_offset(
        self,
        order_by: Optional[str],
        limit: Optional[int],
        offset: Optional[int],
    ) -> str:
        """
        order_by supports:
          - "id" => ORDER BY id ASC
          - "-id" => ORDER BY id DESC
          - "event_time DESC"
          - "event_time ASC"
          - "event_time DESC, id DESC"  (multi-column)

        Notes:
        - This is still an ADT-friendly interface: caller does NOT pass raw SQL beyond
          a constrained ORDER BY expression.
        - We validate identifiers to reduce injection risk.
        """
        sql_parts: List[str] = []

        if order_by:
            ob = order_by.strip()
            if not ob:
                raise ValueError("order_by cannot be empty")

            order_terms: List[str] = []

            for raw_term in ob.split(","):
                term = raw_term.strip()
                if not term:
                    continue

                # Support "-col" shorthand
                if term.startswith("-"):
                    col = term[1:].strip()
                    direction = "DESC"
                    if not col:
                        raise ValueError("order_by contains invalid characters")
                else:
                    # Support "col" or "col ASC/DESC"
                    parts = term.split()
                    if len(parts) == 1:
                        col = parts[0]
                        direction = "ASC"
                    elif len(parts) == 2:
                        col = parts[0]
                        direction = parts[1].upper()
                        if direction not in ("ASC", "DESC"):
                            raise ValueError("order_by direction must be ASC or DESC")
                    else:
                        raise ValueError("order_by format is invalid")

                # allow backticks around identifiers
                col_clean = col.strip()
                if col_clean.startswith("`") and col_clean.endswith("`") and len(col_clean) >= 3:
                    col_clean = col_clean[1:-1]

                # strict identifier validation: letters/numbers/underscore only
                if not re.fullmatch(r"[A-Za-z0-9_]+", col_clean):
                    raise ValueError("order_by contains invalid characters")

                order_terms.append(f"{col_clean} {direction}")

            if order_terms:
                sql_parts.append(" ORDER BY " + ", ".join(order_terms))

        if limit is not None:
            if limit <= 0:
                raise ValueError("limit must be > 0")
            sql_parts.append(" LIMIT %s")

        if offset is not None:
            if offset < 0:
                raise ValueError("offset must be >= 0")
            # MySQL requires LIMIT when using OFFSET; enforce it.
            if limit is None:
                raise ValueError("offset requires limit")
            sql_parts.append(" OFFSET %s")

        return "".join(sql_parts)

    # ---------------------------------
    # SELECT
    # ---------------------------------

    def select(
        self,
        tbname: str,
        filters: Optional[Dict[str, Any]] = None,
        *,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        filters example (equality AND only):
        {"id": 5, "name": "adar"}

        order_by:
          "id" or "-id" or "event_time DESC" or "event_time DESC, id DESC"

        limit/offset optional (offset requires limit).
        """
        filters = filters or {}

        where_sql, values = self._build_where(filters)
        tail_sql = self._build_order_limit_offset(order_by, limit, offset)

        query = f"SELECT * FROM {tbname}{where_sql}{tail_sql}"

        # add limit/offset parameters at the end
        if limit is not None:
            values.append(limit)
        if offset is not None:
            values.append(offset)

        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query, tuple(values))
            return cursor.fetchall()
        finally:
            cursor.close()

    # ---------------------------------
    # INSERT
    # ---------------------------------

    def insert(self, tbname: str, data: Dict[str, Any]) -> Optional[int]:
        if not data:
            raise ValueError("insert() requires data")

        cols = list(data.keys())
        for c in cols:
            if not str(c).replace("_", "").isalnum():
                raise ValueError("insert key contains invalid characters")

        placeholders = ", ".join(["%s"] * len(cols))
        columns_sql = ", ".join(cols)
        values = [data[c] for c in cols]

        query = f"INSERT INTO {tbname} ({columns_sql}) VALUES ({placeholders})"

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, tuple(values))
            self.connection.commit()
            return cursor.lastrowid
        finally:
            cursor.close()

    # ---------------------------------
    # UPDATE
    # ---------------------------------

    def update(self, tbname: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        if not data:
            raise ValueError("update() requires data")
        if not where:
            raise ValueError("update() requires where")

        set_parts: List[str] = []
        values: List[Any] = []
        for k, v in data.items():
            if not str(k).replace("_", "").isalnum():
                raise ValueError("update key contains invalid characters")
            set_parts.append(f"{k}=%s")
            values.append(v)

        where_sql, where_values = self._build_where(where)
        values.extend(where_values)

        query = f"UPDATE {tbname} SET " + ", ".join(set_parts) + where_sql

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, tuple(values))
            self.connection.commit()
            return cursor.rowcount
        finally:
            cursor.close()

    # ---------------------------------
    # DELETE
    # ---------------------------------

    def delete(self, tbname: str, where: Dict[str, Any]) -> int:
        if not where:
            raise ValueError("delete() requires where")

        where_sql, values = self._build_where(where)
        query = f"DELETE FROM {tbname}{where_sql}"

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, tuple(values))
            self.connection.commit()
            return cursor.rowcount
        finally:
            cursor.close()

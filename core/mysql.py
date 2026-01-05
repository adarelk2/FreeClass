# core/mysql.py
from __future__ import annotations

from typing import Optional, Any, Dict, List, Tuple
import re
import mysql.connector
from mysql.connector import MySQLConnection
from core.interfaces.db import DB

class MySQL(DB):
    """
    Minimal MySQL wrapper with:
    - insert/update/delete
    - select with ADT-style filters + safe-ish order_by + limit/offset
    - auto reconnect + single retry on transient connection drops
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
        self._cfg = dict(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            ssl_required=ssl_required,
        )
        self.connection: MySQLConnection = self._connect()

    # -----------------------------
    # CONNECTION
    # -----------------------------

    def _connect(self) -> MySQLConnection:
        conn: MySQLConnection = mysql.connector.connect(
            host=self._cfg["host"],
            user=self._cfg["user"],
            password=self._cfg["password"],
            database=self._cfg["database"],
            port=self._cfg["port"],
            ssl_disabled=(not self._cfg["ssl_required"]),
        )
        conn.autocommit = True  # you already rely on autocommit behavior
        return conn

    def ensure_connection(self) -> None:
        """
        Make sure connection is alive.
        mysql-connector supports ping(reconnect=True)
        """
        try:
            if self.connection is None:  # type: ignore[truthy-bool]
                self.connection = self._connect()
                return
            self.connection.ping(reconnect=True, attempts=1, delay=0)
        except Exception:
            self.connection = self._connect()

    def _validate_tbname(self, tbname: str) -> None:
        # prevent SQL injection via table name
        if not re.fullmatch(r"[A-Za-z0-9_]+", tbname):
            raise ValueError("table name contains invalid characters")

    def _execute_with_retry(
        self,
        query: str,
        params: Tuple[Any, ...],
        *,
        dictionary: bool,
        fetch: bool,
        commit: bool,
    ):
        """
        Execute with:
        - ensure_connection()
        - retry exactly once if the socket/connection dropped
        """
        last_exc: Optional[Exception] = None

        for attempt in (1, 2):
            try:
                self.ensure_connection()
                cursor = self.connection.cursor(dictionary=dictionary)
                try:
                    cursor.execute(query, params)
                    if fetch:
                        return cursor.fetchall()
                    if commit:
                        # In practice autocommit is True, but keep this safe.
                        self.connection.commit()
                    return cursor.rowcount, getattr(cursor, "lastrowid", None)
                finally:
                    cursor.close()
            except Exception as exc:
                last_exc = exc
                if attempt == 1:
                    # reconnect and retry once
                    try:
                        self.connection = self._connect()
                    except Exception:
                        pass
                    continue
                raise

        if last_exc:
            raise last_exc

    # ---------------------------------
    # INTERNAL HELPERS
    # ---------------------------------

    def _build_where(self, filters: Dict[str, Any]) -> Tuple[str, List[Any]]:
        if not filters:
            return "", []

        parts: List[str] = []
        values: List[Any] = []
        for k, v in filters.items():
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

                if term.startswith("-"):
                    col = term[1:].strip()
                    direction = "DESC"
                    if not col:
                        raise ValueError("order_by contains invalid characters")
                else:
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

                col_clean = col.strip()
                if col_clean.startswith("`") and col_clean.endswith("`") and len(col_clean) >= 3:
                    col_clean = col_clean[1:-1]

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
        self._validate_tbname(tbname)
        filters = filters or {}

        where_sql, values = self._build_where(filters)
        tail_sql = self._build_order_limit_offset(order_by, limit, offset)
        query = f"SELECT * FROM {tbname}{where_sql}{tail_sql}"

        if limit is not None:
            values.append(limit)
        if offset is not None:
            values.append(offset)

        rows = self._execute_with_retry(
            query,
            tuple(values),
            dictionary=True,
            fetch=True,
            commit=False,
        )
        return rows

    # ---------------------------------
    # INSERT
    # ---------------------------------

    def insert(self, tbname: str, data: Dict[str, Any]) -> Optional[int]:
        self._validate_tbname(tbname)

        if not data:
            raise ValueError("insert() requires data")

        cols = list(data.keys())
        for c in cols:
            if not str(c).replace("_", "").isalnum():
                raise ValueError("insert key contains invalid characters")

        placeholders = ", ".join(["%s"] * len(cols))
        columns_sql = ", ".join(cols)
        values = tuple(data[c] for c in cols)

        query = f"INSERT INTO {tbname} ({columns_sql}) VALUES ({placeholders})"

        _, lastrowid = self._execute_with_retry(
            query,
            values,
            dictionary=False,
            fetch=False,
            commit=True,
        )
        return lastrowid

    # ---------------------------------
    # UPDATE
    # ---------------------------------

    def update(self, tbname: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        self._validate_tbname(tbname)

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

        rowcount, _ = self._execute_with_retry(
            query,
            tuple(values),
            dictionary=False,
            fetch=False,
            commit=True,
        )
        return int(rowcount)

    # ---------------------------------
    # DELETE
    # ---------------------------------

    def delete(self, tbname: str, where: Dict[str, Any]) -> int:
        self._validate_tbname(tbname)

        if not where:
            raise ValueError("delete() requires where")

        where_sql, values = self._build_where(where)
        query = f"DELETE FROM {tbname}{where_sql}"

        rowcount, _ = self._execute_with_retry(
            query,
            tuple(values),
            dictionary=False,
            fetch=False,
            commit=True,
        )
        return int(rowcount)

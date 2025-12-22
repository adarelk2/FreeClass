# core/mysql.py
from __future__ import annotations

from typing import Optional, Any, Dict, List, Tuple

import mysql.connector
from mysql.connector import MySQLConnection


class MySQL:
    """
    Minimal MySQL connection wrapper.

    Notes:
    - Supports managed DBs (e.g., Aiven) with SSL and connection timeout.
    - Provides CRUD helpers: select/insert/update/delete.
    - select() supports simple equality AND filters (Dict[str, Any]).
    """

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        port: int = 3306,
        *,
        connection_timeout: int = 10,
        ssl_required: bool = True,
    ) -> None:
        self._host = host
        self._user = user
        self._password = password
        self._database = database
        self._port = port

        self._connection_timeout = connection_timeout
        self._ssl_required = ssl_required

        self._conn: Optional[MySQLConnection] = None

    def connect(self) -> None:
        """Opens a connection if not connected."""
        if self._conn is not None and self._conn.is_connected():
            return

        kwargs: Dict[str, Any] = {
            "host": self._host,
            "user": self._user,
            "password": self._password,
            "database": self._database,
            "port": self._port,
            "connection_timeout": self._connection_timeout,
        }

        # For managed DBs (Aiven etc.) TLS is usually required.
        if self._ssl_required:
            # mysql-connector uses TLS by default if available,
            # but we force "not disabled" to avoid accidental plaintext.
            kwargs["ssl_disabled"] = False

        self._conn = mysql.connector.connect(**kwargs)

    def close(self) -> None:
        """Closes the connection if open."""
        if self._conn is None:
            return

        if self._conn.is_connected():
            self._conn.close()

        self._conn = None

    @property
    def connection(self) -> MySQLConnection:
        """Exposes the raw connection. Ensures connection exists before returning."""
        self.connect()
        assert self._conn is not None
        return self._conn

    # ---------------------------------
    # helpers
    # ---------------------------------

    def _build_where(self, filters: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """
        Builds WHERE clause using equality AND only.
        Returns: (where_sql, values)
        """
        where_clauses: List[str] = []
        values: List[Any] = []

        for column, value in filters.items():
            where_clauses.append(f"{column} = %s")
            values.append(value)

        if not where_clauses:
            return "", []

        return " WHERE " + " AND ".join(where_clauses), values

    def _build_order_limit_offset(
        self,
        order_by: Optional[str],
        limit: Optional[int],
        offset: Optional[int],
    ) -> str:
        """
        order_by:
          - "id" => ORDER BY id ASC
          - "-id" => ORDER BY id DESC
        """
        sql_parts: List[str] = []

        if order_by:
            direction = "ASC"
            col = order_by
            if order_by.startswith("-"):
                direction = "DESC"
                col = order_by[1:]
            # naive validation: allow only simple identifier chars
            if not col.replace("_", "").isalnum():
                raise ValueError("order_by contains invalid characters")
            sql_parts.append(f" ORDER BY {col} {direction}")

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
    # UPDATE
    # ---------------------------------

    def update(
        self,
        tbname: str,
        filter: Dict[str, Any],
        where: Dict[str, Any],
    ) -> int:
        """
        filter (SET) example:
        {"name": "test", "age": 27}

        where example:
        {"id": 5}

        Returns:
            number of affected rows
        """
        if not filter:
            raise ValueError("UPDATE requires at least one field to update")
        if not where:
            raise ValueError("UPDATE without WHERE is not allowed")

        set_clauses: List[str] = []
        where_clauses: List[str] = []
        values: List[Any] = []

        for column, value in filter.items():
            set_clauses.append(f"{column} = %s")
            values.append(value)

        for column, value in where.items():
            where_clauses.append(f"{column} = %s")
            values.append(value)

        set_sql = ", ".join(set_clauses)
        where_sql = " AND ".join(where_clauses)

        query = f"UPDATE {tbname} SET {set_sql} WHERE {where_sql}"

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, tuple(values))
            self.connection.commit()
            return cursor.rowcount
        finally:
            cursor.close()

    # ---------------------------------
    # INSERT
    # ---------------------------------

    def insert(
        self,
        tbname: str,
        data: Dict[str, Any],
    ) -> Optional[int]:
        """
        data example:
        {"name": "test", "age": 27}

        Returns:
            last inserted id (if available)
        """
        if not data:
            raise ValueError("INSERT requires at least one field")

        columns: List[str] = []
        placeholders: List[str] = []
        values: List[Any] = []

        for column, value in data.items():
            columns.append(column)
            placeholders.append("%s")
            values.append(value)

        query = f"INSERT INTO {tbname} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, tuple(values))
            self.connection.commit()
            return cursor.lastrowid
        finally:
            cursor.close()

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
          "id" or "-id"

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
    # DELETE
    # ---------------------------------

    def delete(
        self,
        tbname: str,
        where: Dict[str, Any],
    ) -> int:
        """
        Safe delete: WHERE is mandatory.
        where example:
        {"id": 5}

        Returns:
            number of affected rows
        """
        if not where:
            raise ValueError("DELETE without WHERE is not allowed")

        where_sql, values = self._build_where(where)
        query = f"DELETE FROM {tbname}{where_sql}"

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, tuple(values))
            self.connection.commit()
            return cursor.rowcount
        finally:
            cursor.close()

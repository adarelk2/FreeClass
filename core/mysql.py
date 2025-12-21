# core/mysql.py
from __future__ import annotations

from typing import Optional, Any, Dict

import mysql.connector
from mysql.connector import MySQLConnection


class MySQL:
    """
    Minimal MySQL connection wrapper.

    Current:
    - connect / close only
    - select/insert/update will be added next

    Notes:
    - Supports managed DBs (e.g., Aiven) with SSL and connection timeout.
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
        """
        Opens a connection if not connected.
        """
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
        """
        Closes the connection if open.
        """
        if self._conn is None:
            return

        if self._conn.is_connected():
            self._conn.close()

        self._conn = None

    @property
    def connection(self) -> MySQLConnection:
        """
        Exposes the raw connection (useful internally later).
        Ensures connection exists before returning.
        """
        self.connect()
        assert self._conn is not None
        return self._conn

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
        filter example (SET):
        {
            "name": "test",
            "age": 27
        }

        where example (WHERE):
        {
            "userid": 5
        }

        Returns:
            number of affected rows
        """

        if not filter:
            raise ValueError("UPDATE requires at least one field to update")

        if not where:
            raise ValueError("UPDATE without WHERE is not allowed")

        set_clauses = []
        where_clauses = []
        values = []

        # SET part
        for column, value in filter.items():
            set_clauses.append(f"{column} = %s")
            values.append(value)

        # WHERE part
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
        {
            "name": "test",
            "age": 27
        }

        Returns:
            last inserted id (if available)
        """

        if not data:
            raise ValueError("INSERT requires at least one field")

        columns = []
        placeholders = []
        values = []

        for column, value in data.items():
            columns.append(column)
            placeholders.append("%s")
            values.append(value)

        columns_sql = ", ".join(columns)
        placeholders_sql = ", ".join(placeholders)

        query = f"INSERT INTO {tbname} ({columns_sql}) VALUES ({placeholders_sql})"

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, tuple(values))
            self.connection.commit()
            return cursor.lastrowid
        finally:
            cursor.close()

    def select(
        self,
        tbname: str,
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        filters example:
        {
            "userid": 5,
            "name": "adar"
        }
        """

        where_clauses: List[str] = []
        values: List[Any] = []

        for column, value in filters.items():
            where_clauses.append(f"{column} = %s")
            values.append(value)

        where_sql = ""
        if where_clauses:
            where_sql = " WHERE " + " AND ".join(where_clauses)

        query = f"SELECT * FROM {tbname}{where_sql}"

        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query, tuple(values))
            return cursor.fetchall()
        finally:
            cursor.close()

        
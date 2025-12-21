# core/mysql.py
from __future__ import annotations

from typing import Optional

import mysql.connector
from mysql.connector import MySQLConnection


class MySQL:
    """
    Minimal MySQL connection wrapper.

    For now:
    - Connect / close only
    - select/insert/update will be added next
    """

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        port: int = 3306,
    ) -> None:
        self._host = host
        self._user = user
        self._password = password
        self._database = database
        self._port = port

        self._conn: Optional[MySQLConnection] = None

    def connect(self) -> None:
        """
        Opens a connection if not connected.
        """
        if self._conn is not None and self._conn.is_connected():
            return

        self._conn = mysql.connector.connect(
            host=self._host,
            user=self._user,
            password=self._password,
            database=self._database,
            port=self._port,
        )

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

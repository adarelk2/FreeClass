# tests/test_mysql_unittest.py
import sys
from pathlib import Path

# allow running directly: python3 tests/test_mysql_unittest.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import unittest
from unittest.mock import MagicMock, patch
import importlib.util


def load_module_from_path(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module spec for {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestMySQLWrapper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        project_root = Path(__file__).resolve().parents[1]
        mysql_path = project_root / "core" / "mysql.py"
        if not mysql_path.exists():
            raise FileNotFoundError(f"Missing file: {mysql_path}")

        cls.mysql_mod = load_module_from_path("core_mysql_loaded", mysql_path)
        cls.MySQL = cls.mysql_mod.MySQL

    def _make_fake_connection(self):
        conn = MagicMock(name="MySQLConnectionMock")
        conn.is_connected.return_value = True

        cursor = MagicMock(name="CursorMock")
        cursor.rowcount = 1
        cursor.lastrowid = 123
        cursor.fetchall.return_value = [{"id": 1, "name": "adar"}]

        def cursor_factory(*args, **kwargs):
            return cursor

        conn.cursor.side_effect = cursor_factory
        return conn, cursor

    def test_connect_sets_ssl_disabled_when_ssl_required_true(self):
        fake_conn, _ = self._make_fake_connection()

        with patch.object(self.mysql_mod.mysql.connector, "connect", return_value=fake_conn) as mock_connect:
            db = self.MySQL(host="h", user="u", password="p", database="d", port=1, ssl_required=True)
            db.connect()

            called_kwargs = mock_connect.call_args.kwargs
            self.assertIn("ssl_disabled", called_kwargs)
            self.assertFalse(called_kwargs["ssl_disabled"])

    def test_connect_does_not_force_ssl_disabled_when_ssl_required_false(self):
        fake_conn, _ = self._make_fake_connection()

        with patch.object(self.mysql_mod.mysql.connector, "connect", return_value=fake_conn) as mock_connect:
            db = self.MySQL(host="h", user="u", password="p", database="d", port=1, ssl_required=False)
            db.connect()

            called_kwargs = mock_connect.call_args.kwargs
            self.assertNotIn("ssl_disabled", called_kwargs)

    def test_connection_property_auto_connects(self):
        fake_conn, _ = self._make_fake_connection()

        with patch.object(self.mysql_mod.mysql.connector, "connect", return_value=fake_conn):
            db = self.MySQL(host="h", user="u", password="p", database="d", port=1)
            self.assertIs(db.connection, fake_conn)

    def test_close_closes_only_if_connected(self):
        fake_conn, _ = self._make_fake_connection()
        fake_conn.is_connected.return_value = True

        with patch.object(self.mysql_mod.mysql.connector, "connect", return_value=fake_conn):
            db = self.MySQL(host="h", user="u", password="p", database="d", port=1)
            db.connect()
            db.close()

            fake_conn.close.assert_called_once()
            self.assertIsNone(db._conn)

    def test_update_builds_query_and_commits(self):
        fake_conn, cursor = self._make_fake_connection()
        cursor.rowcount = 7

        with patch.object(self.mysql_mod.mysql.connector, "connect", return_value=fake_conn):
            db = self.MySQL(host="h", user="u", password="p", database="d", port=1)

            affected = db.update("test_table", {"name": "adar", "age": 27}, {"id": 1})

            expected_query = "UPDATE test_table SET name = %s, age = %s WHERE id = %s"
            cursor.execute.assert_called_once_with(expected_query, ("adar", 27, 1))
            fake_conn.commit.assert_called_once()
            cursor.close.assert_called_once()
            self.assertEqual(affected, 7)

    def test_insert_builds_query_and_returns_lastrowid(self):
        fake_conn, cursor = self._make_fake_connection()
        cursor.lastrowid = 999

        with patch.object(self.mysql_mod.mysql.connector, "connect", return_value=fake_conn):
            db = self.MySQL(host="h", user="u", password="p", database="d", port=1)

            last_id = db.insert("test_table", {"name": "adar2"})

            expected_query = "INSERT INTO test_table (name) VALUES (%s)"
            cursor.execute.assert_called_once_with(expected_query, ("adar2",))
            fake_conn.commit.assert_called_once()
            cursor.close.assert_called_once()
            self.assertEqual(last_id, 999)

    def test_select_with_filters_builds_where_clause(self):
        fake_conn, cursor = self._make_fake_connection()
        cursor.fetchall.return_value = [{"id": 1, "name": "adar"}]

        with patch.object(self.mysql_mod.mysql.connector, "connect", return_value=fake_conn):
            db = self.MySQL(host="h", user="u", password="p", database="d", port=1)

            rows = db.select("test_table", {"id": 1, "name": "adar"})

            expected_query = "SELECT * FROM test_table WHERE id = %s AND name = %s"
            cursor.execute.assert_called_once_with(expected_query, (1, "adar"))
            self.assertEqual(rows, [{"id": 1, "name": "adar"}])


if __name__ == "__main__":
    unittest.main(verbosity=2)

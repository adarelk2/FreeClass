# core/mocks/mock_json_db.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from copy import deepcopy

from core.interfaces.db import DB


class MockJSONDB(DB):
    """
    JSON-backed mock database.

    Structure:
    {
        "table_name": [
            {"id": 1, "col": "value"},
            {"id": 2, "col": "value"}
        ]
    }
    """

    def __init__(self, json_path: Optional[str] = None) -> None:
        self._path = Path(json_path) if json_path else None
        self._data: Dict[str, List[Dict[str, Any]]] = {}
        self._pk_counter: Dict[str, int] = {}

        if self._path and self._path.exists():
            self._load()

    # -----------------------------
    # INTERNAL
    # -----------------------------
    def printDB(self):
        print(self._data)
        
    def _load(self) -> None:
        raw = json.loads(self._path.read_text())
        self._data = raw
        for table, rows in raw.items():
            max_id = max((row.get("id", 0) for row in rows), default=0)
            self._pk_counter[table] = max_id

    def _save(self) -> None:
        if self._path:
            self._path.write_text(json.dumps(self._data, indent=2))

    def _table(self, name: str) -> List[Dict[str, Any]]:
        if name not in self._data:
            self._data[name] = []
            self._pk_counter[name] = 0
        return self._data[name]

    def _match(self, row: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        return all(row.get(k) == v for k, v in filters.items())

    # -----------------------------
    # SELECT
    # -----------------------------

    def select(
        self,
        tbname: str,
        filters: Optional[Dict[str, Any]] = None,
        *,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:

        rows = deepcopy(self._table(tbname))
        filters = filters or {}

        if filters:
            rows = [r for r in rows if self._match(r, filters)]

        if order_by:
            reverse = False
            key = order_by.strip()
            if key.startswith("-"):
                reverse = True
                key = key[1:]
            rows.sort(key=lambda r: r.get(key), reverse=reverse)

        if offset is not None:
            rows = rows[offset:]

        if limit is not None:
            rows = rows[:limit]

        return rows

    # -----------------------------
    # INSERT
    # -----------------------------

    def insert(self, tbname: str, data: Dict[str, Any]) -> int:
        table = self._table(tbname)

        self._pk_counter[tbname] += 1
        row_id = self._pk_counter[tbname]

        row = {"id": row_id, **data}
        table.append(row)

        self._save()
        return row_id

    # -----------------------------
    # UPDATE
    # -----------------------------

    def update(self, tbname: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        table = self._table(tbname)
        updated = 0

        for row in table:
            if self._match(row, where):
                row.update(data)
                updated += 1

        if updated:
            self._save()

        return updated

    # -----------------------------
    # DELETE
    # -----------------------------

    def delete(self, tbname: str, where: Dict[str, Any]) -> int:
        table = self._table(tbname)
        original_len = len(table)

        table[:] = [r for r in table if not self._match(r, where)]

        deleted = original_len - len(table)
        if deleted:
            self._save()

        return deleted
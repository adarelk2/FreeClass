# core/model_base.py
from __future__ import annotations
from typing import Any, Dict, List, Optional


class ModelBase:
    def __init__(self, _tbname) -> None:
        self.TABLE = _tbname

    def filter(
        self,
        where: Optional[Dict[str, Any]] = None,
        *,
        order_by: Optional[str] = None,
        limit: Optional[int] = 200,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        ADT-style filter wrapper.

        - where: equality AND only, e.g. {"id": 1}
        - order_by: supports "id", "-id", "event_time DESC", "event_time DESC, id DESC"
        - limit/offset: pagination (offset requires limit)
        """
        return self.db.select(
            self.TABLE,
            where or {},
            order_by=order_by,
            limit=limit,
            offset=offset,
        )

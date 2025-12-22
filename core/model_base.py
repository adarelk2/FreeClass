# core/model_base.py
from __future__ import annotations
from typing import Any, Dict, List, Optional

class ModelBase:
    def __init__(self, _tbname) -> None:
        self.TABLE = _tbname

    def filter(self, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return self.db.select(self.TABLE, where or {})

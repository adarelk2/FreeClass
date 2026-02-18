from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from models.User import User


class UsersRepository(ABC):
    TABLE = "users"

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def get_all(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_with_filter(
        self,
        where: Optional[Dict[str, Any]] = None,
        *,
        order_by: Optional[str] = None,
        limit: Optional[int] = 200,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def update_by_id(self, building_id: int, fields: Dict[str, Any]) -> int:
        pass

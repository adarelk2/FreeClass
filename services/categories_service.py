# services/categories_service.py
from __future__ import annotations
from typing import Optional, Dict, Any
from core.infrastructure.mysql import MySQL
from repositories.class_room_categories_repository import ClassRoomCategoriesRepository

class CategoriesService:
    """
    Service for room category operations.
    
    Responsibilities:
    - List categories
    - Get category by ID
    - Create/update categories
    """
    
    def __init__(
        self,
        db_instance: Optional[MySQL] = None,
        categories_model: Optional[ClassRoomCategoriesRepository] = None,
    ):
        self.db = db_instance
        self.categories_model = categories_model
    
    def list_all(self) -> list:
        """Get all categories"""
        return self.categories_model.get_all()
    
    def get_by_id(self, category_id: int) -> Optional[Dict[str, Any]]:
        """Get category by ID"""
        return self.categories_model.get_by_id(category_id)
    
    def create(self, data: Dict[str, Any]) -> int:
        """Create a new category"""
        if not data:
            raise ValueError("create() requires data")
        return self.categories_model.create(data)

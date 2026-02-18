# services/users_service.py
from __future__ import annotations
from typing import Optional, Dict, Any
from core.infrastructure.mysql import MySQL
from repositories.users_repository import UsersRepository

class UsersService:
    """
    Service for user authentication and management.
    
    Responsibilities:
    - Authenticate user by username/password
    - Get user by ID
    - Manage user data
    """
    
    def __init__(
        self,
        db_instance: Optional[MySQL] = None,
        users_model: Optional[UsersRepository] = None,
    ):
        self.db = db_instance
        self.users_model = users_model
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user by username and password.
        
        Returns: User dict if found and password matches, None otherwise
        """
        if not username or not password:
            return None
        
        users = self.users_model.get_with_filter({"username": username, "password": password})
        
        if users and len(users) > 0:
            return users[0]
        
        return None
    
    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return self.users_model.get_by_id(user_id)
    
    def filter(self, query: Dict[str, Any] = None) -> list:
        """Get all users or filter by conditions"""
        if query is None:
            query = {}
        return self.users_model.get_with_filter(query)

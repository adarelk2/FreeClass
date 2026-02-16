# core/permissions.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class Permissions(ABC):
    """
    Abstract permissions interface for managing role-based access control.
    
    Implementations should handle checking which roles have access to which controllers/features.
    """

    @abstractmethod
    def get_permissions(self, controller: str, filters: Optional[Dict] = None) -> List[str]:
        """
        Get list of allowed roles for a controller.
        
        Args:
            controller: Controller name to check permissions for
            filters: Optional filters dictionary (for compatibility)
        
        Returns:
            List of role names allowed to access this controller
        """
        pass

    @abstractmethod
    def create_new_permission(self, controller: str, roles: List[str]) -> None:
        """
        Create or update permissions for a controller.
        
        Args:
            controller: Controller name
            roles: List of role names to allow access
        """
        pass

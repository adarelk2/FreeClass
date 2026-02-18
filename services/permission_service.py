from typing import List

from models.User import User
from core.permissions import Permissions


class PermissionService:
    def __init__(self, model: Permissions):
        self.model = model

    def get_permissions_by_controller(self, controller: str) -> List[str]:
        return self.model.get_permissions(controller, {})

    def has_permission(self, user: User, controller_name: str) -> bool:
        allowed_roles = self.get_permissions_by_controller(controller_name)

        # If no explicit roles are configured, treat as allowed (open-by-default).
        if not allowed_roles:
            return True

        return user.role in allowed_roles

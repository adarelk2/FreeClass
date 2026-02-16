<<<<<<< Updated upstream
from core.interfaces.user import UserInterface 
from core.interfaces.permissions import Permissions

class PermissionService: 
    def __init__(self, model: Permissions):
        self.model = model
    
    def get_permissions_by_controller(self, controller: str):
        return self.model.get_permissions(controller, {})
    
    def has_permission(self, user: UserInterface, controller_name: str) -> bool:
        allowed_roles = self.get_permissions_by_controller(controller_name)
        
        if not allowed_roles:
            return True 
            
        return user.role in allowed_roles
=======
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from core.permissions import Permissions

>>>>>>> Stashed changes

class PermissionLocal(Permissions):
    """In-memory permissions provider (useful for tests / small apps)."""

    def __init__(self) -> None:
        self.permissions: Dict[str, List[str]] = {"dashboardadmin": ["admin"]}

    def get_permissions(self, controller: str, filters: Optional[Dict] = None) -> List[str]:
        return self.permissions.get(controller, [])

    def create_new_permission(self, controller: str, roles: List[str]) -> None:
        self.permissions[controller] = roles

<<<<<<< Updated upstream
pdb = PermissionLocal()
user1 = UserInterface("Yosef", "admin", 6)
service = PermissionService(pdb)
=======
>>>>>>> Stashed changes

class PermissionDB(Permissions):
    """DB-backed permissions provider.

    Expects a table named `permissions` with rows like:
      {id, controller, roles}
    where `roles` is a JSON array (e.g. '["admin","user"]').

    This implementation works with the project's `MockJSONDB` (table-style)
    and MySQL wrapper (select/insert/update). If the permissions table is
    missing or the DB errors, callers can fallback to `PermissionLocal`.
    """

    def __init__(self, db: Any) -> None:
        self.db = db

    def _read_row(self, controller: str) -> Optional[Dict[str, Any]]:
        try:
            rows = self.db.select("permissions", {"controller": controller})
            if rows:
                return rows[0]
            return None
        except Exception:
            # table may not exist or DB may not support select; signal caller
            raise

    def get_permissions(self, controller: str, filters: Optional[Dict] = None) -> List[str]:
        try:
            row = self._read_row(controller)
        except Exception:
            return []

        if not row:
            return []

        roles_raw = row.get("roles")
        if roles_raw is None:
            return []

        # If stored as JSON string, parse; if list already, return it.
        if isinstance(roles_raw, (list, tuple)):
            return list(roles_raw)

        try:
            return json.loads(roles_raw)
        except Exception:
            # last resort: comma separated
            if isinstance(roles_raw, str):
                return [r.strip() for r in roles_raw.split(",") if r.strip()]
            return []

    def create_new_permission(self, controller: str, roles: List[str]) -> None:
        payload = {"controller": controller, "roles": json.dumps(roles)}
        try:
            # try update first
            updated = self.db.update("permissions", {"roles": json.dumps(roles)}, {"controller": controller})
            if not updated:
                self.db.insert("permissions", payload)
        except Exception:
            # ignore DB errors; caller may fallback to other provider
            raise


__all__ = ["PermissionService", "PermissionLocal", "PermissionDB"]
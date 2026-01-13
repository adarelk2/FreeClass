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

class PermissionLocal(Permissions):
    def __init__(self):
        self.permissions = {"dashboardadmin": ["admin"]}

    def get_permissions(self, controller: str, filters: dict = None):
        return self.permissions.get(controller, [])

    def create_new_permission(self, controller: str, roles: list):
        self.permissions[controller] = roles

pdb = PermissionLocal()
user1 = UserInterface("Yosef", "admin", 6)
service = PermissionService(pdb)

print(service.has_permission(user1, "dashboardadmin"))
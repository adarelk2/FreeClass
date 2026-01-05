from abc import ABC, abstractmethod

class Permissions(ABC):
    @abstractmethod
    def create_new_permission(self):
        pass

    @abstractmethod
    def get_permissions(self):
        pass

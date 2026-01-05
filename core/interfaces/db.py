from abc import ABC, abstractmethod

class DB(ABC):
    @abstractmethod
    def select(self):
        pass

    @abstractmethod
    def insert(self):
        pass

    @abstractmethod
    def update(self):
        pass

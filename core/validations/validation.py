from abc import ABC, abstractmethod
import re

class ValidationInterface(ABC):
    """ממשק מופשט עבור ולידטורים."""

    def __init__(self):
        self.errors = []

    @abstractmethod
    def validate(self, data):
        """מבצע ולידציה על הנתונים שהתקבלו."""
        pass
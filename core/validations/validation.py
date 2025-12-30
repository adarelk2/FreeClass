from abc import ABC, abstractmethod
import re

class ValidationInterface(ABC):
    """ממשק מופשט עבור ולידטורים."""

    def __init__(self, params):
        self.errors = []
        self.params = params

    @abstractmethod
    def validate(self, data):
        """מבצע ולידציה על הנתונים שהתקבלו."""
        pass
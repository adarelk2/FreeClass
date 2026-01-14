from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, Union

@dataclass
class UserInterface:
    username: str
    role: str
    id: Any
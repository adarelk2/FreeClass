# core/controller_loader.py
from __future__ import annotations

import importlib
import os
from typing import Any


class ControllerLoader:
    CONTROLLERS_PACKAGE = "controllers"
    CONTROLLERS_PATH = "controllers"

    def is_controller_exist(self, name: str) -> bool:
        if name.startswith("_"):
            return False

        file_name = f"{name}_controller.py"
        return file_name in os.listdir(self.CONTROLLERS_PATH)

    def get_controller(self, name: str) -> Any:
        if not self.is_controller_exist(name):
            raise KeyError(f"Controller '{name}' not found")

        module_name = f"{self.CONTROLLERS_PACKAGE}.{name}_controller"
        class_name = f"{name.capitalize()}Controller"

        module = importlib.import_module(module_name)

        if not hasattr(module, class_name):
            raise AttributeError(
                f"Class '{class_name}' not found in {module_name}"
            )

        cls = getattr(module, class_name)
        return cls()

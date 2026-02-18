from core.controller_base import ControllerBase
from core.config import SECRET_JWT_KEY
import jwt
import time

class SensorController(ControllerBase):
    def __init__(self, _container):
        self.motion_events_service = _container.motion_events_service

    def createNewActivty(self, params):
        sensor_private_key = params.get("private_key", "private_key")
        if self.motion_events_service.log_sensor_activity(sensor_private_key):
            return self.responseJSON("Done", True)
        return self.responseJSON("Error - sensor not found", False)

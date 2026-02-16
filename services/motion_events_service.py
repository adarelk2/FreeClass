# services/motion_events_service.py
from __future__ import annotations
from typing import Optional, Dict, Any
from core.infrastructure.mysql import MySQL
from repositories.classroom_motion_events_repository import ClassroomMotionEventsRepository
from repositories.sensors_repository import SensorsRepository

class MotionEventsService:
    """
    Service for motion event operations (sensor activity logging).
    
    Responsibilities:
    - Log sensor motion events
    - Get motion events
    - Manage motion event data
    """
    
    def __init__(
        self,
        db_instance: Optional[MySQL] = None,
        motion_events_model: Optional[ClassroomMotionEventsRepository] = None,
        sensors_model: Optional[SensorsRepository] = None,
    ):
        self.db = db_instance
        self.motion_events_model = motion_events_model
        self.sensors_model = sensors_model
    
    def log_sensor_activity(self, sensor_private_key: str) -> bool:
        """
        Log a motion event from a sensor using its private key.
        
        Verifies sensor exists, then creates motion event.
        Returns True if successful, False if sensor not found.
        """
        if not sensor_private_key:
            raise ValueError("sensor_private_key is required")
        
        # Get sensor by private key
        sensor = self.sensors_model.get_by_privateKey(sensor_private_key)
        if sensor is None:
            return False
        
        # Create motion event for this sensor's room
        try:
            self.motion_events_model.create({
                "classroom_id": sensor.get("room_id") if isinstance(sensor, dict) else sensor.room_id,
                "sensor_id": sensor.get("id") if isinstance(sensor, dict) else sensor.id,
            })
            return True
        except Exception:
            return False
    
    def list_by_room(self, room_id: int) -> list:
        """Get all motion events for a specific room"""
        if not room_id:
            raise ValueError("room_id is required")
        return self.motion_events_model.filter({"classroom_id": room_id})
    
    def get_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Get motion event by ID"""
        return self.motion_events_model.get_by_id(event_id)

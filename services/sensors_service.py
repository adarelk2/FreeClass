# services/sensors_service.py
from __future__ import annotations
from typing import Optional, Dict, Any
from core.infrastructure.mysql import MySQL
from repositories.sensors_repository import SensorsRepository
from repositories.classrooms_repository import ClassroomsRepository

class SensorsService:
    """
    Service for sensor operations and management.
    
    Responsibilities:
    - Create sensors
    - Get sensor by private key
    - List all sensors
    - Manage sensor data
    """
    
    def __init__(
        self,
        db_instance: Optional[MySQL] = None,
        sensors_model: Optional[SensorsRepository] = None,
        classrooms_model: Optional[ClassroomsRepository] = None,
    ):
        self.db = db_instance
        self.sensors_model = sensors_model
        self.classrooms_model = classrooms_model
    
    def create_sensor(self, room_id: int, private_key: str, public_key: str) -> Optional[int]:
        """
        Create a new sensor for a room.
        
        Validates that room exists before creating.
        Returns sensor ID if successful, None if room doesn't exist.
        """
        if not room_id or not private_key or not public_key:
            raise ValueError("room_id, private_key, and public_key are required")
        
        # Verify room exists
        room = self.classrooms_model.get_by_id(room_id)
        if room is None:
            return None
        
        sensor_id = self.sensors_model.create({
            "room_id": room_id,
            "private_key": private_key,
            "public_key": public_key
        })
        
        return sensor_id
    
    def get_by_private_key(self, private_key: str) -> Optional[Dict[str, Any]]:
        """Get sensor by private key"""
        if not private_key:
            return None
        return self.sensors_model.get_by_privateKey(private_key)
    
    def get_by_id(self, sensor_id: int) -> Optional[Dict[str, Any]]:
        """Get sensor by ID"""
        return self.sensors_model.get_by_id(sensor_id)
    
    def list_all(self) -> list:
        """Get all sensors"""
        return self.sensors_model.filter()
    
    def list_by_room(self, room_id: int) -> list:
        """Get all sensors for a specific room"""
        return self.sensors_model.list_by_room_id(room_id)

from dataclasses import dataclass
from typing import Any, Dict, Optional, Union
from datetime import datetime

@dataclass
class ClassroomMotionEvent:
    id: int
    classroom_id: int
    sensor_id: str
    event_time: datetime
    received_at: datetime
    event_type: str
    confidence: Optional[int]
    payload: Optional[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "classroom_id": self.classroom_id,
            "sensor_id": self.sensor_id,
            "event_time": self.event_time,
            "received_at": self.received_at,
            "event_type": self.event_type,
            "confidence": self.confidence,
            "payload": self.payload,
        }
    
    def get(self, key: str, default=None):
        """Dict-like get method for compatibility"""
        return getattr(self, key, default)
    
    def __str__(self) -> str:
        return f"ClassroomMotionEvent(id={self.id}, classroom_id={self.classroom_id}, event_time={self.event_time})"
    
    def __repr__(self) -> str:
        return self.__str__()

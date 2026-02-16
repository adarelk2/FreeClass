# services/rooms_service.py
from __future__ import annotations
from typing import Optional
from datetime import datetime
from core.config import SENSORE_LOG_ACTIVITY
from core.infrastructure.mysql import MySQL
from repositories.classrooms_repository import ClassroomsRepository
from repositories.classroom_motion_events_repository import ClassroomMotionEventsRepository
from repositories.sensors_repository import SensorsRepository

class RoomsService:
    """
    Room domain logic (availability).

    Rule:
    - Room is BUSY if it has a motion event in the last activity_seconds.
    - Otherwise it's AVAILABLE.

    Public API is kept:
    - getRoomsAvailable()
    - getRoomsAvilable()  (legacy typo alias)
    - getAvailableRoomIds()
    - filterEventsBySec()
    """

    def __init__(
        self,
        db_instance: Optional[MySQL] = None,
        rooms_model: Optional[ClassroomsRepository] = None,
        motion_events_model: Optional[ClassroomMotionEventsRepository] = None,
        sensor_model: Optional[SensorsRepository] = None,
    ):
        self.db = db_instance

        self.activity_seconds = int(SENSORE_LOG_ACTIVITY)
        self.utcnow_fn = datetime.utcnow

        self.rooms_model = rooms_model
        self.motion_events_model = motion_events_model

        self.sensor_model = sensor_model
    # ---- ADT: public API (keep names) ----

    def getRoomsAvailable(self):
        rooms = self.rooms_model.filter()  # [{id, id_building, floor, class_number, ...}, ...]
        events = self.motion_events_model.filter()  # [{classroom_id, event_time, ...}, ...]

        recent_events = self.filterEventsBySec(events, self.activity_seconds)
        busy_ids = self._extract_busy_classroom_ids(recent_events)

        if not busy_ids:
            return list(rooms)

        available_rooms = []
        for r in rooms:
            rid = r.get("id")
            if rid is None:
                available_rooms.append(r)
                continue

            try:
                rid_int = int(rid)
            except Exception:
                available_rooms.append(r)
                continue

            if rid_int not in busy_ids:
                available_rooms.append(r)

        return available_rooms

    def getAvailableRoomIds(self):
        rooms = self.getRoomsAvailable()
        ids = set()

        for room in rooms:
            rid = room.get("id")
            if rid is None:
                continue
            try:
                ids.add(int(rid))
            except Exception:
                continue

        return ids

    def filterEventsBySec(self, _events, _sec):
        now = self.utcnow_fn()
        sec = int(_sec)

        filtered = []
        for ev in _events or []:
            t = ev.get("event_time")
            if not t:
                continue
            try:
                delta = (now - t).total_seconds()
            except Exception:
                continue

            if 0 <= delta <= sec:
                filtered.append(ev)

        return filtered

    # ---- Internals (not part of ADT) ----

    def _extract_busy_classroom_ids(self, events):
        busy = set()
        for ev in events or []:
            cid = ev.get("classroom_id")
            if cid is None:
                continue
            try:
                busy.add(int(cid))
            except Exception:
                continue
        return busy



    def delete_room_by_id(self, classroom_id: int) -> bool:
        """
        Delete a room and all related data (sensors, motion events) in correct order.
        Service orchestrates the cascade, each model deletes its own data.
        
        Returns True if room existed and was deleted, False otherwise
        """
        if not isinstance(classroom_id, int):
            raise TypeError(f"classroom_id must be int, got {type(classroom_id).__name__}")
        
        if classroom_id <= 0:
            raise ValueError("classroom_id must be positive")
        
        # Check if room exists
        check = self.rooms_model.get_by_id(classroom_id)
        if check is None:
            return False
        
        # Delete in order (respecting foreign key constraints)
        # 1. Delete motion events
        self.motion_events_model.delete_events_by_room_id(classroom_id)
        
        # 2. Delete sensors
        self.sensor_model.delete_sensor_by_room_id(classroom_id)
        
        # 3. Delete the classroom itself
        self.rooms_model.delete_room_by_id(classroom_id)
        
        return True

    def list_all(self) -> list:
        """Get all rooms"""
        return self.rooms_model.filter()

    def create_room(self, building_id: int, floor: int, class_number: int, category_id: int = None) -> Optional[int]:
        """
        Create a new room in a building.
        
        Returns room ID if successful, None if building doesn't exist.
        """
        if not building_id:
            raise ValueError("building_id is required")
        
        room_data = {
            "id_building": building_id,
            "floor": floor,
            "class_number": class_number,
        }
        
        if category_id is not None:
            room_data["category"] = category_id
        
        return self.rooms_model.create(room_data)


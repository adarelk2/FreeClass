# services/rooms_service.py
from __future__ import annotations

from datetime import datetime

from core.config import SENSORE_LOG_ACTIVITY
from core.database import db as default_db
from models.classroom_motion_events_model import ClassroomMotionEventsModel
from models.class_rooms_model import ClassRoomsModel
from models.sensors_model import SensorsModel

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

    def __init__(self, db_instance=None, rooms_model=None, motion_events_model=None, activity_seconds=None, utcnow_fn=None):
        self.db = db_instance or default_db

        self.activity_seconds = int(activity_seconds) if activity_seconds is not None else int(SENSORE_LOG_ACTIVITY)
        self.utcnow_fn = utcnow_fn or datetime.utcnow

        self.rooms_model = rooms_model or ClassRoomsModel(self.db)
        self.motion_events_model = motion_events_model or ClassroomMotionEventsModel(self.db)

        self.sensor_model = SensorsModel(self.db)
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



    def delete_room_by_id(self, classroom_id):

        self.sensor_model.delete_sensor_by_room_id(classroom_id)
        self.motion_events_model.delete_events_by_room_id(classroom_id)
        self.rooms_model.delete_room_by_id(classroom_id)

        return True
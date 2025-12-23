# services/rooms_service.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Set, Callable

from core.config import SENSORE_LOG_ACTIVITY
from core.database import db as default_db
from models.classroom_motion_events_model import ClassroomMotionEventsModel
from models.class_rooms_model import ClassRoomsModel


class RoomsService:
    """
    Provides room availability logic (general capability).
    This service should be reusable by multiple screens (dashboard, search, API, etc.).
    """

    def __init__(
        self,
        db_instance: Any = None,
        activity_seconds: Optional[int] = None,
        rooms_model: Optional[ClassRoomsModel] = None,
        motion_events_model: Optional[ClassroomMotionEventsModel] = None,
        utcnow_fn: Callable[[], datetime] = datetime.utcnow,
    ):
        # DI רך: אם לא הזריקו - משתמשים בברירת מחדל כמו שהיה לך
        self.db = db_instance or default_db
        self.activity_seconds = int(activity_seconds) if activity_seconds is not None else int(SENSORE_LOG_ACTIVITY)

        self.rooms_model = rooms_model or ClassRoomsModel(self.db)
        self.motion_events_model = motion_events_model or ClassroomMotionEventsModel(self.db)

        self.utcnow_fn = utcnow_fn

    # ---- ADT: public API (keep names) ----

    def getRoomsAvailable(self) -> List[Dict[str, Any]]:
        """
        Returns list of rooms that are currently available.
        Availability rule: room is BUSY if it has a motion event in the last activity_seconds.
        Otherwise it's AVAILABLE.
        """
        rooms = self.rooms_model.filter()  # [{id, id_building, floor, class_number, ...}, ...]
        events = self.motion_events_model.filter()  # [{classroom_id, event_time, ...}, ...]

        recent_events = self.filterEventsBySec(events, self.activity_seconds)

        busy_ids = self._extract_busy_classroom_ids(recent_events)
        if not busy_ids:
            return list(rooms)

        # Keep only rooms whose id NOT in busy_ids
        available_rooms: List[Dict[str, Any]] = []
        for r in rooms:
            rid = r.get("id")
            if rid is None:
                # חדר בלי id? לא זורקים - אבל גם לא נוכל לסווג אותו כ-busy, נשאיר אותו
                available_rooms.append(r)
                continue

            try:
                rid_int = int(rid)
            except Exception:
                # id לא תקין? נשאיר
                available_rooms.append(r)
                continue

            if rid_int not in busy_ids:
                available_rooms.append(r)

        return available_rooms

    # Alias for backward compatibility (typo in older code)
    def getRoomsAvilable(self) -> List[Dict[str, Any]]:
        return self.getRoomsAvailable()

    def getAvailableRoomIds(self) -> Set[int]:
        """
        Faster helper for dashboards: returns set of available room IDs.
        So you can enrich rooms without duplicating lists.
        """
        rooms = self.getRoomsAvailable()
        ids: Set[int] = set()

        for room in rooms:
            rid = room.get("id")
            if rid is None:
                continue
            try:
                ids.add(int(rid))
            except Exception:
                continue

        return ids

    def filterEventsBySec(self, _events: Iterable[Dict[str, Any]], _sec: int) -> List[Dict[str, Any]]:
        now = self.utcnow_fn()
        sec_int = int(_sec)

        filtered: List[Dict[str, Any]] = []
        for ev in _events:
            ev_time = ev.get("event_time")
            if not ev_time:
                continue

            try:
                diff = (now - ev_time).total_seconds()
            except Exception:
                continue

            if 0 <= diff <= sec_int:
                filtered.append(ev)

        return filtered

    # ---- Internals (not part of ADT) ----

    def _extract_busy_classroom_ids(self, events: Iterable[Dict[str, Any]]) -> Set[int]:
        busy: Set[int] = set()
        for ev in events:
            cid = ev.get("classroom_id")
            if cid is None:
                continue
            try:
                busy.add(int(cid))
            except Exception:
                continue
        return busy

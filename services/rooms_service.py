# services/rooms_service.py
from datetime import datetime
from core.config import SENSORE_LOG_ACTIVITY
from core.database import db
from models.classroom_motion_events_model import ClassroomMotionEventsModel
from models.class_rooms_model import ClassRoomsModel


class RoomsService:
    """
    Provides room availability logic (general capability).
    This service should be reusable by multiple screens (dashboard, search, API, etc.).
    """

    def getRoomsAvailable(self):
        """
        Returns list of room dicts that are available 'now' according to recent motion events.
        Backwards-compatible with your intent (and fixes spelling).
        """
        rooms_model = ClassRoomsModel(db)
        events_model = ClassroomMotionEventsModel(db)

        rooms = rooms_model.filter()          # all rooms
        events = events_model.filter()        # all events

        recent_events = self.filterEventsBySec(events, SENSORE_LOG_ACTIVITY)

        busy_classroom_ids = {
            ev["classroom_id"]
            for ev in recent_events
            if ev.get("classroom_id") is not None
        }

        rooms_available = [
            room for room in rooms
            if room.get("id") not in busy_classroom_ids
        ]

        return rooms_available

    # keep your original misspelled name if other code already calls it
    def getRoomsAvilable(self):
        return self.getRoomsAvailable()

    def getAvailableRoomIds(self) -> set[int]:
        """
        Faster helper for dashboards: returns set of available room IDs.
        So you can enrich rooms without duplicating lists.
        """
        rooms = self.getRoomsAvailable()
        return {room.get("id") for room in rooms if room.get("id") is not None}

    def filterEventsBySec(self, _events, _sec):
        now = datetime.utcnow()

        return [
            ev
            for ev in _events
            if ev.get("event_time")
            and 0 <= (now - ev["event_time"]).total_seconds() <= int(_sec)
        ]

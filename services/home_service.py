# services/home_service.py
from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Dict, List
from datetime import datetime
from core.config import SENSORE_LOG_ACTIVITY
from core.infrastructure.mysql import MySQL
from repositories.building_repository import BuildingRepository
from repositories.classrooms_repository import ClassroomsRepository
from repositories.classroom_motion_events_repository import ClassroomMotionEventsRepository

if TYPE_CHECKING:
    from services.building_service import BuildingService
    from services.rooms_service import RoomsService

class HomeService:
    """
    Thin orchestration service for the /home screen only.

    Responsibilities:
    - Build the exact DTOs the home template expects:
      - buildings cards
      - recent spaces
      - available now
    - Optimize by fetching all data once and reusing it
    """

    def __init__(
        self,
        db_instance: Optional[MySQL] = None,
        building_service: Optional[BuildingService] = None,
        rooms_service: Optional[RoomsService] = None,
        building_model: Optional[BuildingRepository] = None,
        class_room_model: Optional[ClassroomsRepository] = None,
        class_room_motion_events_model: Optional[ClassroomMotionEventsRepository] = None,
    ):
        self.db = db_instance
        self.building_service = building_service
        self.rooms_service = rooms_service
        self.building_model = building_model
        self.class_room_model = class_room_model
        self.class_room_motion_events_model = class_room_motion_events_model
        self.activity_seconds = int(SENSORE_LOG_ACTIVITY)
        self.utcnow_fn = datetime.utcnow

    # -------------------------
    # Debug/Diagnostic Methods
    # -------------------------

    def debug_availability_calculation(self) -> Dict:
        """
        Debug method to understand how rooms are being classified as busy/available.
        Returns detailed info about the calculation.
        """
        now = self.utcnow_fn()
        events = self.class_room_motion_events_model.get_with_filter(order_by="event_time DESC", limit=200)
        buildings = self.building_model.get_all()
        rooms = self.class_room_model.get_all()
        
        # Calculate busy rooms
        busy_ids = set()
        event_details = []
        
        for e in events or []:
            cid = e.get("classroom_id")
            t = e.get("event_time")
            
            if not cid or not t:
                continue
            
            try:
                # Parse timestamp
                if isinstance(t, str):
                    try:
                        event_time = datetime.fromisoformat(t.replace('Z', '+00:00'))
                    except:
                        event_time = datetime.strptime(t[:19], '%Y-%m-%d %H:%M:%S')
                else:
                    event_time = t
                
                # Calculate delta
                delta = (now - event_time).total_seconds()
                is_recent = 0 <= delta <= self.activity_seconds
                
                event_details.append({
                    "classroom_id": cid,
                    "event_time": str(event_time),
                    "now": str(now),
                    "delta_seconds": delta,
                    "activity_window": self.activity_seconds,
                    "is_recent": is_recent,
                })
                
                if is_recent:
                    busy_ids.add(int(cid))
            except Exception as ex:
                event_details.append({
                    "classroom_id": cid,
                    "event_time": str(t),
                    "error": str(ex),
                })
        
        # Calculate available rooms
        available_ids = set()
        for r in rooms:
            rid = self._to_int(r.get("id"))
            if rid is not None and rid not in busy_ids:
                available_ids.add(rid)
        
        return {
            "total_events": len(events or []),
            "total_rooms": len(rooms),
            "activity_window_seconds": self.activity_seconds,
            "busy_room_count": len(busy_ids),
            "available_room_count": len(available_ids),
            "busy_room_ids": sorted(list(busy_ids)),
            "available_room_ids": sorted(list(available_ids)),
            "event_details": event_details[:10],  # First 10 events
        }

    # -------------------------
    # Internal data cache
    # -------------------------

    def _calculate_available_room_ids(self, events: List[Dict]) -> set:
        """
        Calculate available room IDs from motion events.
        RULE: Room is AVAILABLE by default. Only BUSY if recent motion event (within activity_seconds).
        """
        # Get all rooms first
        all_rooms = self.class_room_model.get_all()
        all_room_ids = set()
        for r in all_rooms:
            rid = self._to_int(r.get("id"))
            if rid is not None:
                all_room_ids.add(rid)
        
        # If no events, all rooms are available
        if not events:
            return all_room_ids
        
        now = self.utcnow_fn()
        busy_ids = set()
        activity_window = int(self.activity_seconds) if self.activity_seconds else 900

        for e in events:
            try:
                cid = e.get("classroom_id")
                if cid is None:
                    continue

                # Parse event time
                t = e.get("event_time")
                if not t:
                    continue
                
                if isinstance(t, str):
                    # Try ISO format first
                    try:
                        event_time = datetime.fromisoformat(t.replace('Z', '+00:00'))
                    except:
                        # Fall back to MySQL datetime format
                        try:
                            event_time = datetime.strptime(t[:19], '%Y-%m-%d %H:%M:%S')
                        except:
                            continue
                else:
                    event_time = t
                
                # Calculate time delta
                delta = (now - event_time).total_seconds()
                
                # Mark room as BUSY only if event is within activity window
                if 0 <= delta <= activity_window:
                    busy_ids.add(int(cid))
            except:
                # Skip problematic events, don't mark room as busy
                continue

        # Available rooms = All rooms - Busy rooms
        available_ids = all_room_ids - busy_ids
        return available_ids

    def _prepare_home_data(self) -> Dict:
        """
        Fetch all base data once for the home page.
        Returns a dictionary with all needed data to avoid duplicate queries.
        """
        # Single queries for all base data
        buildings = self.building_model.get_all()
        rooms = self.class_room_model.get_all()
        events = self.class_room_motion_events_model.get_with_filter(order_by="event_time DESC", limit=200)

        # Calculate available room IDs from events
        available_ids = self._calculate_available_room_ids(events)

        # Index lookups for fast access
        rooms_by_id = {}
        for r in rooms:
            rid = self._to_int(r.get("id"))
            if rid is not None:
                rooms_by_id[rid] = r

        buildings_by_id = {}
        for b in buildings:
            bid = self._to_int(b.get("id"))
            if bid is not None:
                buildings_by_id[bid] = b

        # Build room-building relationships
        rooms_by_building = {}
        for r in rooms:
            b_id = self._to_int(r.get("id_building"))
            if b_id is not None:
                rooms_by_building.setdefault(b_id, []).append(r)

        return {
            "buildings": buildings,
            "rooms": rooms,
            "events": events,
            "available_ids": available_ids,
            "rooms_by_id": rooms_by_id,
            "buildings_by_id": buildings_by_id,
            "rooms_by_building": rooms_by_building,
        }

    # -------------------------
    # helpers
    # -------------------------

    def _to_int(self, value):
        if value is None:
            return None
        try:
            return int(value)
        except Exception:
            return None

    def _building_display_name(self, b):
        bid = b.get("id")
        return b.get("building_name") or b.get("name") or (f"Building {bid}" if bid is not None else "Unknown")

    # -------------------------
    # DTOs for /home (all use cached data)
    # -------------------------

    def getHomeBuildingsCards(self, cached_data: Optional[Dict] = None):
        """Build building cards with availability counts."""
        if cached_data is None:
            cached_data = self._prepare_home_data()

        buildings = cached_data["buildings"]
        rooms_by_building = cached_data["rooms_by_building"]
        available_ids = cached_data["available_ids"]

        cards = []
        for b in buildings:
            b_id = self._to_int(b.get("id"))
            rooms = rooms_by_building.get(b_id, []) if b_id is not None else []

            total_rooms = len(rooms)
            available_rooms = sum(1 for r in rooms if self._to_int(r.get("id")) in available_ids)

            cards.append(
                {
                    "id": b.get("id"),
                    "name": self._building_display_name(b),
                    "availableRooms": available_rooms,
                    "totalRooms": total_rooms,
                    "floors": b.get("floors"),
                    "color": b.get("color") or "#000",
                }
            )

        return cards

    def getHomeRecentSpaces(self, limit=4, cached_data: Optional[Dict] = None):
        """Get recent spaces that had motion events."""
        limit_int = self._to_int(limit) or 0
        if limit_int <= 0:
            return []

        if cached_data is None:
            cached_data = self._prepare_home_data()

        events = cached_data["events"]
        rooms_by_id = cached_data["rooms_by_id"]
        buildings_by_id = cached_data["buildings_by_id"]
        available_ids = cached_data["available_ids"]

        seen = set()
        items = []

        for e in events:
            classroom_id = self._to_int(e.get("classroom_id"))
            if classroom_id is None or classroom_id in seen:
                continue
            seen.add(classroom_id)

            room = rooms_by_id.get(classroom_id, {}) or {}
            b_id = self._to_int(room.get("id_building"))

            building_name = "Unknown"
            if b_id is not None:
                b = buildings_by_id.get(b_id, {}) or {}
                building_name = self._building_display_name(b)

            class_number = room.get("class_number") or room.get("number") or room.get("id") or classroom_id
            status = "available" if classroom_id in available_ids else "busy"

            items.append(
                {
                    "id": classroom_id,
                    "name": f"כיתה {class_number}",
                    "building": building_name,
                    "status": status,
                }
            )

            if len(items) >= limit_int:
                break

        return items

    def getHomeAvailableNow(self, limit=3, cached_data: Optional[Dict] = None):
        """Get rooms that are available right now."""
        limit_int = self._to_int(limit) or 0
        if limit_int <= 0:
            return []

        if cached_data is None:
            cached_data = self._prepare_home_data()

        buildings = cached_data["buildings"]
        rooms_by_id = cached_data["rooms_by_id"]
        rooms_by_building = cached_data["rooms_by_building"]
        available_ids = cached_data["available_ids"]

        available = []
        for b in buildings:
            b_id = self._to_int(b.get("id"))
            b_name = self._building_display_name(b)
            rooms = rooms_by_building.get(b_id, []) if b_id is not None else []

            for r in rooms:
                rid = self._to_int(r.get("id"))
                if rid is None or rid not in available_ids:
                    continue

                class_number = r.get("class_number") or r.get("number") or r.get("id")
                floor_int = self._to_int(r.get("floor")) or 0

                available.append(
                    {
                        "name": f"כיתה {class_number}",
                        "building": b_name,
                        "floor": floor_int,
                    }
                )

        available.sort(key=lambda x: (x.get("floor", 0), str(x.get("name", ""))))
        return available[:limit_int]

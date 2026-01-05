# services/home_service.py
from __future__ import annotations

class HomeService:
    """
    Thin orchestration service for the /home screen only.

    Responsibilities:
    - Build the exact DTOs the home template expects:
      - buildings cards
      - recent spaces
      - available now
    """

    def __init__(self, db_instance=None, building_service=None, rooms_service=None ,building_model = None ,class_room_model = None ,class_room_motion_events_model = None):
        self.db = db_instance
        self.building_service = building_service
        self.rooms_service = rooms_service
        self.building_model = building_model
        self.class_room_model = class_room_model
        self.class_room_motion_events_model =class_room_motion_events_model
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
    # DTOs for /home
    # -------------------------

    def getHomeBuildingsCards(self):
        buildings = self.building_service.get_buildings_with_rooms(include_availability=True)

        cards = []
        for b in buildings:
            rooms = b.get("rooms", []) or []

            total_rooms = len(rooms)
            available_rooms = 0
            for r in rooms:
                if r.get("is_available") is True:
                    available_rooms += 1

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

    def getHomeRecentSpaces(self, limit=4):
        limit_int = self._to_int(limit) or 0
        if limit_int <= 0:
            return []

        batch_limit = max(20, limit_int * 10)

        events = self.class_room_motion_events_model.filter(order_by="event_time DESC", limit=batch_limit)

        # Lookups
        rooms = self.class_room_model.filter()
        buildings = self.building_model.filter()

        rooms_by_id = {}
        for r in rooms:
            rid = self._to_int(r.get("id"))
            if rid is None:
                continue
            rooms_by_id[rid] = r

        buildings_by_id = {}
        for b in buildings:
            bid = self._to_int(b.get("id"))
            if bid is None:
                continue
            buildings_by_id[bid] = b

        available_ids = set(self.rooms_service.getAvailableRoomIds() or [])

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

    def getHomeAvailableNow(self, limit=3):
        limit_int = self._to_int(limit) or 0
        if limit_int <= 0:
            return []

        buildings = self.building_service.get_buildings_with_rooms(include_availability=True)

        available = []
        for b in buildings:
            b_name = self._building_display_name(b)
            rooms = b.get("rooms", []) or []

            for r in rooms:
                if r.get("is_available") is not True:
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

# services/dashboard_service.py
from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.database import db as default_db
from models.building_model import BuildingModel
from models.class_rooms_model import ClassRoomsModel
from services.rooms_service import RoomsService


class DashboardService:
    """
    Dashboard/Home orchestration service:
    builds the object the page needs (buildings + rooms inside each building).
    """

    def __init__(
        self,
        db_instance: Any = None,
        building_model: Optional[BuildingModel] = None,
        classrooms_model: Optional[ClassRoomsModel] = None,
        rooms_service: Optional[RoomsService] = None,
    ):
        self.db = db_instance or default_db

        self.building_model = building_model or BuildingModel(self.db)
        self.classrooms_model = classrooms_model or ClassRoomsModel(self.db)

        # ✅ RoomsService בלי ארגומנטים – תואם ADT
        self.rooms_service = rooms_service or RoomsService()

    # ---- ADT: public API (keep names) ----

    def getBuildingsList(self):
        return self.building_model.filter()

    def getBuildingsWithRooms(self, include_availability: bool = True):
        """
        Returns:
        [
          {
            ...building fields...,
            "rooms": [
              {...room fields..., "is_available": bool}
            ]
          }
        ]
        """
        buildings = self.building_model.filter()
        rooms = self.classrooms_model.filter()

        available_ids = self._get_available_ids(include_availability)
        rooms_by_building = self._index_rooms_by_building(rooms)

        result: List[Dict[str, Any]] = []
        for b in buildings:
            b_id_int = self._safe_int(b.get("id"))
            building_rooms = rooms_by_building.get(b_id_int, []) if b_id_int is not None else []

            b_copy = dict(b)
            b_copy["rooms"] = self._enrich_rooms(building_rooms, available_ids, include_availability)
            result.append(b_copy)

        return result

    def getBuildingWithRoomsById(self, building_id: int, include_availability: bool = True) -> Optional[Dict[str, Any]]:
        """
        Returns a single building object enriched with its rooms:
          {
            ...building fields...,
            "rooms": [
              {...room fields..., "is_available": bool}
            ]
          }

        If building not found => returns None.

        Notes:
        - Uses filter() and in-memory filtering to avoid changing Model ADT.
        """
        building_id_int = self._safe_int(building_id)
        if building_id_int is None:
            return None

        # Find the building
        building = self._find_building_by_id(building_id_int)
        if building is None:
            return None

        # Collect only rooms for this building (single pass)
        rooms = self.classrooms_model.filter()
        building_rooms: List[Dict[str, Any]] = []
        for r in rooms:
            if self._safe_int(r.get("id_building")) == building_id_int:
                building_rooms.append(r)

        available_ids = self._get_available_ids(include_availability)

        b_copy = dict(building)
        b_copy["rooms"] = self._enrich_rooms(building_rooms, available_ids, include_availability)
        return b_copy

    # ----------------------------
    # Home page DTO builders
    # ----------------------------

    def getHomeBuildingsCards(self):
        buildings = self.getBuildingsWithRooms(include_availability=True)
        cards = []

        for b in buildings:
            b_id = b.get("id")
            rooms = b.get("rooms", []) or []

            total_rooms = len(rooms)
            available_rooms = sum(1 for r in rooms if r.get("is_available") is True)

            color = b.get("color") or "#000"

            cards.append({
                "id": b_id,
                "name": b.get("building_name") or b.get("name") or f"Building {b_id}",
                "availableRooms": available_rooms,
                "totalRooms": total_rooms,
                "floors": b.get("floors"),
                "color": color,
            })

        return cards

    def getHomeRecentSpaces(self, limit: int = 4):
        """
        Returns list for recentSpaces_server:
        [
          { id, name, building, status }
        ]

        "recent" is based on the latest rows in classroom_motion_events (event_time DESC),
        deduped by classroom_id.
        """
        try:
            from models.classroom_motion_events_model import ClassroomMotionEventsModel
        except Exception:
            return self._fallback_recent_spaces(limit)

        limit_int = max(0, int(limit))
        batch_limit = max(20, limit_int * 10)

        motion_model = ClassroomMotionEventsModel(self.db)
        events = motion_model.filter(order_by="event_time DESC", limit=batch_limit)

        rooms = self.classrooms_model.filter()
        buildings = self.building_model.filter()

        rooms_by_id = self._index_by_int_id(rooms)
        buildings_by_id = self._index_by_int_id(buildings)

        available_ids = self.rooms_service.getAvailableRoomIds()
        available_ids_int = {self._safe_int(x) for x in available_ids}
        available_ids_int.discard(None)

        seen_classroom_ids = set()
        items: List[Dict[str, Any]] = []

        for e in events:
            classroom_id_int = self._safe_int(e.get("classroom_id"))
            if classroom_id_int is None:
                continue

            if classroom_id_int in seen_classroom_ids:
                continue
            seen_classroom_ids.add(classroom_id_int)

            room = rooms_by_id.get(classroom_id_int, {}) or {}
            building_name = self._resolve_building_name(room, buildings_by_id)

            class_number = room.get("class_number") or room.get("number") or room.get("id")
            status = "available" if (classroom_id_int in available_ids_int) else "busy"

            items.append({
                "id": classroom_id_int,
                "name": f"כיתה {class_number}",
                "building": building_name,
                "status": status,
            })

            if limit_int and len(items) >= limit_int:
                break

        return items

    def getHomeAvailableNow(self, limit: int = 3):
        buildings = self.getBuildingsWithRooms(include_availability=True)

        available: List[Dict[str, Any]] = []
        for b in buildings:
            b_name = b.get("building_name") or b.get("name") or "Unknown"
            rooms = b.get("rooms", []) or []

            for r in rooms:
                if r.get("is_available") is not True:
                    continue

                class_number = r.get("class_number") or r.get("number") or r.get("id")
                floor_int = self._safe_int(r.get("floor")) or 0

                available.append({
                    "name": f"כיתה {class_number}",
                    "building": b_name,
                    "floor": floor_int,
                })

        available.sort(key=lambda x: (x.get("floor", 0), str(x.get("name", ""))))
        return available[:max(0, int(limit))]

    # ----------------------------
    # Internals (private helpers) - does not change ADT
    # ----------------------------

    def _safe_int(self, value: Any) -> Optional[int]:
        try:
            if value is None:
                return None
            return int(value)
        except Exception:
            return None

    def _get_available_ids(self, include_availability: bool):
        if not include_availability:
            return set()
        return self.rooms_service.getAvailableRoomIds()

    def _enrich_rooms(self, rooms: List[Dict[str, Any]], available_ids: set, include_availability: bool):
        enriched: List[Dict[str, Any]] = []
        for r in rooms:
            r_copy = dict(r)
            if include_availability:
                r_copy["is_available"] = (r_copy.get("id") in available_ids)
            enriched.append(r_copy)
        return enriched

    def _index_rooms_by_building(self, rooms: List[Dict[str, Any]]):
        rooms_by_building: Dict[int, List[Dict[str, Any]]] = {}
        for room in rooms:
            b_id_int = self._safe_int(room.get("id_building"))
            if b_id_int is None:
                continue
            rooms_by_building.setdefault(b_id_int, []).append(room)
        return rooms_by_building

    def _find_building_by_id(self, building_id_int: int) -> Optional[Dict[str, Any]]:
        buildings = self.building_model.filter()
        for b in buildings:
            if self._safe_int(b.get("id")) == building_id_int:
                return b
        return None

    def _index_by_int_id(self, rows: List[Dict[str, Any]]):
        by_id: Dict[int, Dict[str, Any]] = {}
        for row in rows:
            rid = self._safe_int(row.get("id"))
            if rid is None:
                continue
            by_id[rid] = row
        return by_id

    def _resolve_building_name(self, room: Dict[str, Any], buildings_by_id: Dict[int, Dict[str, Any]]) -> str:
        b_id_int = self._safe_int(room.get("id_building"))
        if b_id_int is None:
            return "Unknown"
        b = buildings_by_id.get(b_id_int, {}) or {}
        return b.get("building_name") or b.get("name") or "Unknown"

    def _fallback_recent_spaces(self, limit: int = 4):
        rooms = self.classrooms_model.filter()
        buildings = self.building_model.filter()

        buildings_by_id = self._index_by_int_id(buildings)

        available_ids = self.rooms_service.getAvailableRoomIds()
        items: List[Dict[str, Any]] = []

        for r in rooms:
            rid_int = self._safe_int(r.get("id"))
            if rid_int is None:
                continue

            building_name = self._resolve_building_name(r, buildings_by_id)

            class_number = r.get("class_number") or r.get("number") or rid_int
            status = "available" if (rid_int in available_ids) else "busy"

            items.append({
                "id": rid_int,
                "name": f"כיתה {class_number}",
                "building": building_name,
                "status": status,
            })

        items.sort(key=lambda x: x.get("id", 0), reverse=True)
        return items[:max(0, int(limit))]

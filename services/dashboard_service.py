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

        self.rooms_service = rooms_service or RoomsService(self.db)

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
        buildings = self.building_model.filter()     # all buildings
        rooms = self.classrooms_model.filter()       # all rooms

        available_ids = set()
        if include_availability:
            available_ids = self.rooms_service.getAvailableRoomIds()

        rooms_by_building: Dict[int, List[Dict[str, Any]]] = {}
        for room in rooms:
            b_id = room.get("id_building")
            if b_id is None:
                continue
            try:
                b_id_int = int(b_id)
            except Exception:
                continue
            rooms_by_building.setdefault(b_id_int, []).append(room)

        result = []
        for b in buildings:
            b_id = b.get("id")

            b_copy = dict(b)
            enriched_rooms: List[Dict[str, Any]] = []

            if b_id is not None:
                try:
                    b_id_int = int(b_id)
                except Exception:
                    b_id_int = None

                building_rooms = rooms_by_building.get(b_id_int, []) if b_id_int is not None else []
                for r in building_rooms:
                    r_copy = dict(r)
                    if include_availability:
                        r_copy["is_available"] = (r_copy.get("id") in available_ids)
                    enriched_rooms.append(r_copy)

            b_copy["rooms"] = enriched_rooms
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
        - If you add BuildingModel.getById / findOne later, we can optimize without changing this ADT.
        """
        try:
            building_id_int = int(building_id)
        except Exception:
            return None

        # bring buildings and find the requested one
        buildings = self.building_model.filter()
        building: Optional[Dict[str, Any]] = None
        for b in buildings:
            bid = b.get("id")
            if bid is None:
                continue
            try:
                if int(bid) == building_id_int:
                    building = b
                    break
            except Exception:
                continue

        if building is None:
            return None

        # get rooms for this building
        rooms = self.classrooms_model.filter()
        building_rooms: List[Dict[str, Any]] = []
        for r in rooms:
            b_id = r.get("id_building")
            if b_id is None:
                continue
            try:
                if int(b_id) == building_id_int:
                    building_rooms.append(r)
            except Exception:
                continue

        available_ids = set()
        if include_availability:
            available_ids = self.rooms_service.getAvailableRoomIds()

        enriched_rooms: List[Dict[str, Any]] = []
        for r in building_rooms:
            r_copy = dict(r)
            if include_availability:
                r_copy["is_available"] = (r_copy.get("id") in available_ids)
            enriched_rooms.append(r_copy)

        b_copy = dict(building)
        b_copy["rooms"] = enriched_rooms
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
            available_rooms = 0
            for r in rooms:
                if r.get("is_available") is True:
                    available_rooms += 1

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
        try:
            from models.classroom_motion_events_model import ClassroomMotionEventsModel
        except Exception:
            rooms = self.classrooms_model.filter()
            buildings = self.building_model.filter()

            buildings_by_id = {}
            for b in buildings:
                bid = b.get("id")
                if bid is None:
                    continue
                try:
                    buildings_by_id[int(bid)] = b
                except Exception:
                    continue

            available_ids = self.rooms_service.getAvailableRoomIds()
            items = []
            for r in rooms:
                rid = r.get("id")
                if rid is None:
                    continue
                try:
                    rid_int = int(rid)
                except Exception:
                    continue

                b_id = r.get("id_building")
                b_name = "Unknown"
                if b_id is not None:
                    try:
                        b_name = (buildings_by_id.get(int(b_id), {}) or {}).get("building_name") \
                                 or (buildings_by_id.get(int(b_id), {}) or {}).get("name") \
                                 or "Unknown"
                    except Exception:
                        pass

                class_number = r.get("class_number") or r.get("number") or rid_int
                status = "available" if (rid_int in available_ids) else "busy"

                items.append({
                    "id": rid_int,
                    "name": f"כיתה {class_number}",
                    "building": b_name,
                    "status": status,
                })

            def _id_as_int(x):
                try:
                    return int(x.get("id") or 0)
                except Exception:
                    return 0

            items.sort(key=_id_as_int, reverse=True)
            return items[:max(0, int(limit))]

        limit_int = max(0, int(limit))
        batch_limit = max(20, limit_int * 10)

        motion_model = ClassroomMotionEventsModel(self.db)
        events = motion_model.filter(order_by="event_time DESC", limit=batch_limit)

        rooms = self.classrooms_model.filter()
        buildings = self.building_model.filter()

        rooms_by_id: Dict[int, Dict[str, Any]] = {}
        for r in rooms:
            rid = r.get("id")
            if rid is None:
                continue
            try:
                rooms_by_id[int(rid)] = r
            except Exception:
                continue

        buildings_by_id: Dict[int, Dict[str, Any]] = {}
        for b in buildings:
            bid = b.get("id")
            if bid is None:
                continue
            try:
                buildings_by_id[int(bid)] = b
            except Exception:
                continue

        available_ids = self.rooms_service.getAvailableRoomIds()
        available_ids_int = set()
        for x in available_ids:
            try:
                available_ids_int.add(int(x))
            except Exception:
                pass

        seen_classroom_ids = set()
        items = []

        for e in events:
            classroom_id = e.get("classroom_id")
            if classroom_id is None:
                continue

            try:
                classroom_id_int = int(classroom_id)
            except Exception:
                continue

            if classroom_id_int in seen_classroom_ids:
                continue
            seen_classroom_ids.add(classroom_id_int)

            room = rooms_by_id.get(classroom_id_int, {}) or {}
            building_name = "Unknown"
            b_id = room.get("id_building")

            if b_id is not None:
                try:
                    b = buildings_by_id.get(int(b_id), {}) or {}
                    building_name = b.get("building_name") or b.get("name") or "Unknown"
                except Exception:
                    pass

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

        available = []
        for b in buildings:
            b_name = b.get("building_name") or b.get("name") or "Unknown"
            rooms = b.get("rooms", []) or []

            for r in rooms:
                if r.get("is_available") is not True:
                    continue

                class_number = r.get("class_number") or r.get("number") or r.get("id")
                floor = r.get("floor")

                try:
                    floor_int = int(floor) if floor is not None else 0
                except Exception:
                    floor_int = 0

                available.append({
                    "name": f"כיתה {class_number}",
                    "building": b_name,
                    "floor": floor_int,
                })

        available.sort(key=lambda x: (x.get("floor", 0), str(x.get("name", ""))))
        return available[:max(0, int(limit))]

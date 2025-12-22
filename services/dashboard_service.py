# services/dashboard_service.py
from core.database import db
from models.building_model import BuildingModel
from models.class_rooms_model import ClassRoomsModel
from services.rooms_service import RoomsService


class DashboardService:
    """
    Dashboard/Home orchestration service:
    builds the object the page needs (buildings + rooms inside each building).
    """

    def getBuildingsList(self):
        building_model = BuildingModel(db)
        return building_model.filter()

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

        building_model = BuildingModel(db)
        rooms_model = ClassRoomsModel(db)

        buildings = building_model.filter()   # all buildings
        rooms = rooms_model.filter()          # all rooms

        available_ids = set()
        if include_availability:
            available_ids = RoomsService().getAvailableRoomIds()

        # group rooms by building id
        rooms_by_building: dict[int, list] = {}
        for room in rooms:
            b_id = room.get("id_building")
            if b_id is None:
                continue
            rooms_by_building.setdefault(int(b_id), []).append(room)

        # attach rooms into each building
        result = []
        for b in buildings:
            b_id = b.get("id")
            if b_id is None:
                # still return it, but no rooms
                b_copy = dict(b)
                b_copy["rooms"] = []
                result.append(b_copy)
                continue

            b_id_int = int(b_id)
            building_rooms = rooms_by_building.get(b_id_int, [])

            # enrich rooms for UI if needed
            enriched_rooms = []
            for r in building_rooms:
                r_copy = dict(r)
                if include_availability:
                    r_copy["is_available"] = (r_copy.get("id") in available_ids)
                enriched_rooms.append(r_copy)

            b_copy = dict(b)
            b_copy["rooms"] = enriched_rooms
            result.append(b_copy)

        return result

    # ----------------------------
    # Home page DTO builders
    # ----------------------------

    def getHomeBuildingsCards(self):
        """
        Returns list for buildings_server:
        [
          { id, name, availableRooms, totalRooms, color }
        ]
        """
        buildings = self.getBuildingsWithRooms(include_availability=True)
        cards = []

        for b in buildings:
            b_id = b.get("id")
            rooms = b.get("rooms", []) or []

            total_rooms = len(rooms)
            available_rooms = 0
            for r in rooms:
                if bool(r.get("is_available")):
                    available_rooms += 1

            # color now comes from DB (buildings.color)
            color = b.get("color") or "#000"

            cards.append({
                "id": b_id,
                "name": b.get("building_name") or b.get("name") or f"Building {b_id}",
                "availableRooms": available_rooms,
                "totalRooms": total_rooms,
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
        deduped by classroom_id (so a noisy sensor won't flood the list).
        """

        # Import lazily to avoid breaking startup if the model file isn't present yet.
        try:
            from models.classroom_motion_events_model import ClassroomMotionEventsModel
        except Exception:
            # fallback: old heuristic (by room id) if motion-events model isn't available
            buildings = self.getBuildingsWithRooms(include_availability=True)

            items = []
            for b in buildings:
                b_name = b.get("building_name") or b.get("name") or "Unknown"
                rooms = b.get("rooms", []) or []
                for r in rooms:
                    room_id = r.get("id")
                    class_number = r.get("class_number") or r.get("number") or room_id
                    status = "available" if bool(r.get("is_available")) else "busy"
                    items.append({
                        "id": room_id,
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

        # We intentionally pull a bigger batch than limit, because we dedup by classroom_id.
        limit_int = max(0, int(limit))
        batch_limit = max(20, limit_int * 10)

        motion_model = ClassroomMotionEventsModel(db)
        events = motion_model.filter(order_by="event_time DESC", limit=batch_limit)

        # Build maps to enrich: room -> building
        rooms_model = ClassRoomsModel(db)
        building_model = BuildingModel(db)

        rooms = rooms_model.filter()
        buildings = building_model.filter()

        rooms_by_id = {}
        for r in rooms:
            rid = r.get("id")
            if rid is None:
                continue
            try:
                rooms_by_id[int(rid)] = r
            except Exception:
                continue

        buildings_by_id = {}
        for b in buildings:
            bid = b.get("id")
            if bid is None:
                continue
            try:
                buildings_by_id[int(bid)] = b
            except Exception:
                continue

        # availability set (same logic as your getBuildingsWithRooms)
        available_ids = RoomsService().getAvailableRoomIds()
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

            room = rooms_by_id.get(classroom_id_int)
            if not room:
                continue

            b_id = room.get("id_building")
            try:
                b_id_int = int(b_id) if b_id is not None else 0
            except Exception:
                b_id_int = 0

            building = buildings_by_id.get(b_id_int, {})
            building_name = building.get("building_name") or building.get("name") or "Unknown"

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
        """
        Returns list for available_now_server:
        [
          { name, building, floor }
        ]
        """
        buildings = self.getBuildingsWithRooms(include_availability=True)

        available = []
        for b in buildings:
            b_name = b.get("building_name") or b.get("name") or "Unknown"
            rooms = b.get("rooms", []) or []

            for r in rooms:
                if not bool(r.get("is_available")):
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

        # "available now" ordering: lowest floor first then by name
        available.sort(key=lambda x: (x.get("floor", 0), str(x.get("name", ""))))
        return available[:max(0, int(limit))]

# services/building_service.py
from __future__ import annotations

class BuildingService:
    """
    Domain service for buildings.

    Responsibilities:
    - Fetch buildings
    - Fetch rooms and attach them to buildings
    - Optionally enrich rooms with availability using RoomsService

    Notes:
    - No UI/"home page" DTOs here.
    - Public API is intentionally small and reusable.
    """

    def __init__(self, db_instance=None, building_model=None, classrooms_model=None, rooms_service=None):
        self.db = db_instance
        self.building_model = building_model
        self.classrooms_model = classrooms_model
        self.rooms_service = rooms_service

    # -------------------------
    # Small internal helpers
    # -------------------------

    def _to_int(self, value):
        if value is None:
            return None
        try:
            return int(value)
        except Exception:
            return None

    def _group_rooms_by_building(self, rooms):
        by_building = {}
        for r in rooms:
            b_id = self._to_int(r.get("id_building"))
            if b_id is None:
                continue
            by_building.setdefault(b_id, []).append(r)
        return by_building

    def _enrich_rooms(self, rooms, include_availability, available_ids):
        if not rooms:
            return []

        if not include_availability:
            return [dict(r) for r in rooms]

        enriched = []
        for r in rooms:
            r_copy = dict(r)
            rid = self._to_int(r_copy.get("id"))
            r_copy["is_available"] = (rid in available_ids) if rid is not None else False
            enriched.append(r_copy)
        return enriched

    # -------------------------
    # Public API (domain)
    # -------------------------
    def get_buildings_by_ids(self, building_ids):
        ids = [self._to_int(x) for x in building_ids if self._to_int(x) is not None]
        if not ids:
            return []

        all_buildings = self.building_model.filter()
        return [b for b in all_buildings if self._to_int(b.get("id")) in ids]

    def _attach_rooms_to_buildings(self, buildings, rooms, include_availability, available_ids):
        rooms_by_building = self._group_rooms_by_building(rooms)

        result = []
        for b in buildings:
            b_id = self._to_int(b.get("id"))
            b_copy = dict(b)

            building_rooms = rooms_by_building.get(b_id, []) if b_id is not None else []
            b_copy["rooms"] = self._enrich_rooms(building_rooms, include_availability, available_ids)

            result.append(b_copy)

        return result


    def get_buildings_with_rooms(self, building_ids=None, include_availability=True):
        # Backward-compat: allow get_buildings_with_rooms(True/False)
        if isinstance(building_ids, bool):
            include_availability = building_ids
            building_ids = None

        if building_ids is None:
            buildings = self.building_model.filter()
        else:
            buildings = self.get_buildings_by_ids(building_ids)

        rooms = self.classrooms_model.filter()
        available_ids = self.rooms_service.getAvailableRoomIds() if include_availability else []

        return self._attach_rooms_to_buildings(buildings, rooms, include_availability, available_ids)

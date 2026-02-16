# services/building_service.py
from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from core.infrastructure.mysql import MySQL
from repositories.building_repository import BuildingRepository
from repositories.classrooms_repository import ClassroomsRepository

if TYPE_CHECKING:
    from services.rooms_service import RoomsService

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

    def __init__(
        self,
        db_instance: Optional[MySQL] = None,
        building_model: Optional[BuildingRepository] = None,
        classrooms_model: Optional[ClassroomsRepository] = None,
        rooms_service: Optional[RoomsService] = None,
    ):
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

    def delete_building_by_id(self, building_id: int) -> bool:
        """
        Delete a building and all related data (classrooms, sensors, motion events) in correct order.
        Uses bulk deletes for efficiency (4 queries instead of N*3).
        
        Returns True if building existed and was deleted, False otherwise
        """
        if not isinstance(building_id, int):
            raise TypeError(f"building_id must be int, got {type(building_id).__name__}")
        
        if building_id <= 0:
            raise ValueError("building_id must be positive")
        
        # Check if building exists
        check = self.building_model.get_by_id(building_id)
        if check is None:
            return False
        
        # Delete in order (respecting foreign key constraints)
        # 1. Delete all motion events for rooms in this building
        self.rooms_service.motion_events_model.delete_events_by_building_id(building_id)
        
        # 2. Delete all sensors for rooms in this building
        self.rooms_service.sensor_model.delete_sensors_by_building_id(building_id)
        
        # 3. Delete all classrooms in this building
        self.classrooms_model.delete_rooms_by_building_id(building_id)
        
        # 4. Delete the building itself
        self.building_model.delete_building_by_id(building_id)
        
        return True

    def get_building_by_id(self, building_id: int) -> Optional[dict]:
        """Get building by ID"""
        return self.building_model.get_by_id(building_id)

    def create_building(self, building_name: str, floors: int, color: str = "#000") -> Optional[int]:
        """
        Create a new building.
        
        Returns building ID if successful.
        """
        if not building_name:
            raise ValueError("building_name is required")
        
        building_id = self.building_model.create({
            "building_name": building_name,
            "floors": floors,
            "color": color,
        })
        
        return building_id




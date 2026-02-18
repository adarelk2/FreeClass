import unittest
from datetime import datetime, timedelta

from core.infrastructure.mock_json_db import MockJSONDB
from repositories.building_repository_mock import BuildingRepositoryMock
from repositories.classrooms_repository_mock import ClassroomsRepositoryMock
from repositories.classroom_motion_events_repository_mock import ClassroomMotionEventsRepositoryMock
from repositories.sensors_repository_mock import SensorsRepositoryMock
from services.rooms_service import RoomsService
from services.building_service import BuildingService


class TestUS2BuildingCardData(unittest.TestCase):
    def test_building_card_data(self):
        db = MockJSONDB()
        buildings = BuildingRepositoryMock(db)
        rooms = ClassroomsRepositoryMock(db)
        events = ClassroomMotionEventsRepositoryMock(db)
        sensors = SensorsRepositoryMock(db)

        building_id = buildings.create({"building_name": "Engineering", "floors": 3, "color": "#000"})
        room_a = rooms.create({"id_building": building_id, "floor": 1, "class_number": 101, "category": 1})
        room_b = rooms.create({"id_building": building_id, "floor": 2, "class_number": 202, "category": 1})

        events.create({
            "classroom_id": room_b,
            "sensor_id": "s-2",
            "event_time": datetime.utcnow() - timedelta(seconds=30),
        })

        rooms_service = RoomsService(db, rooms, events, sensors)
        service = BuildingService(None, buildings, rooms, rooms_service)

        result = service.get_buildings_with_rooms()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["building_name"], "Engineering")
        room_flags = {r["id"]: r["is_available"] for r in result[0]["rooms"]}
        self.assertTrue(room_flags[room_a])
        self.assertFalse(room_flags[room_b])

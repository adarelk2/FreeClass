import unittest
from datetime import datetime, timedelta

from core.infrastructure.mock_json_db import MockJSONDB
from repositories.building_repository_mock import BuildingRepositoryMock
from repositories.classrooms_repository_mock import ClassroomsRepositoryMock
from repositories.classroom_motion_events_repository_mock import ClassroomMotionEventsRepositoryMock
from services.home_service import HomeService


class TestUS6AvailableNow(unittest.TestCase):
    def test_available_now(self):
        db = MockJSONDB()
        buildings = BuildingRepositoryMock(db)
        rooms = ClassroomsRepositoryMock(db)
        events = ClassroomMotionEventsRepositoryMock(db)

        building_id = buildings.create({"building_name": "Main", "floors": 2, "color": "#abc"})
        busy_room = rooms.create({"id_building": building_id, "floor": 1, "class_number": 11, "category": 1})
        rooms.create({"id_building": building_id, "floor": 2, "class_number": 22, "category": 1})

        events.create(
            {
                "classroom_id": busy_room,
                "sensor_id": "s-2",
                "event_time": datetime.utcnow() - timedelta(seconds=45),
            }
        )

        service = HomeService(
            None,
            building_service=None,
            rooms_service=None,
            building_model=buildings,
            class_room_model=rooms,
            class_room_motion_events_model=events,
        )

        available = service.getHomeAvailableNow(limit=10)
        names = {item["name"] for item in available}

        self.assertIn("כיתה 22", names)
        self.assertNotIn("כיתה 11", names)

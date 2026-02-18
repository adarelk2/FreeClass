import unittest
from datetime import datetime, timedelta

from core.infrastructure.mock_json_db import MockJSONDB
from repositories.building_repository_mock import BuildingRepositoryMock
from repositories.classrooms_repository_mock import ClassroomsRepositoryMock
from repositories.classroom_motion_events_repository_mock import ClassroomMotionEventsRepositoryMock
from services.home_service import HomeService


class TestUS5RecentActivityList(unittest.TestCase):
    def test_recent_activity_list(self):
        db = MockJSONDB()
        buildings = BuildingRepositoryMock(db)
        rooms = ClassroomsRepositoryMock(db)
        events = ClassroomMotionEventsRepositoryMock(db)

        building_id = buildings.create({"building_name": "Science", "floors": 4, "color": "#123"})
        room_id = rooms.create({"id_building": building_id, "floor": 1, "class_number": 606, "category": 1})

        events.create(
            {
                "classroom_id": room_id,
                "sensor_id": "s-1",
                "event_time": datetime.utcnow() - timedelta(seconds=20),
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

        recent = service.getHomeRecentSpaces(limit=5)

        self.assertIsInstance(recent, list)
        self.assertGreaterEqual(len(recent), 1)

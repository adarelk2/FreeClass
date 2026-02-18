import unittest
from datetime import datetime, timedelta

from core.infrastructure.mock_json_db import MockJSONDB
from repositories.classrooms_repository_mock import ClassroomsRepositoryMock
from repositories.classroom_motion_events_repository_mock import ClassroomMotionEventsRepositoryMock
from repositories.sensors_repository_mock import SensorsRepositoryMock
from services.rooms_service import RoomsService


class TestUS1TotalVacancyCounter(unittest.TestCase):
    def test_total_vacancy_counter(self):
        db = MockJSONDB()
        rooms = ClassroomsRepositoryMock(db)
        events = ClassroomMotionEventsRepositoryMock(db)
        sensors = SensorsRepositoryMock(db)

        busy_room_id = rooms.create({"id_building": 1, "floor": 1, "class_number": 101, "category": 1})
        free_room_id = rooms.create({"id_building": 1, "floor": 1, "class_number": 102, "category": 1})

        events.create(
            {
                "classroom_id": busy_room_id,
                "sensor_id": "s-1",
                "event_time": datetime.utcnow() - timedelta(seconds=30),
            }
        )

        service = RoomsService(None, rooms, events, sensors)
        available_ids = service.getAvailableRoomIds()

        self.assertIn(free_room_id, available_ids)
        self.assertNotIn(busy_room_id, available_ids)
        self.assertGreater(len(available_ids), 0)

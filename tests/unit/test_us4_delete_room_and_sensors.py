import unittest
from datetime import datetime

from core.infrastructure.mock_json_db import MockJSONDB
from repositories.classrooms_repository_mock import ClassroomsRepositoryMock
from repositories.classroom_motion_events_repository_mock import ClassroomMotionEventsRepositoryMock
from repositories.sensors_repository_mock import SensorsRepositoryMock
from services.rooms_service import RoomsService


class TestUS4DeleteRoomAndSensors(unittest.TestCase):
    def test_delete_room_and_sensors(self):
        db = MockJSONDB()
        rooms = ClassroomsRepositoryMock(db)
        events = ClassroomMotionEventsRepositoryMock(db)
        sensors = SensorsRepositoryMock(db)

        room_id = rooms.create({"id_building": 1, "floor": 2, "class_number": 201, "category": 1})
        sensors.create({"room_id": room_id, "private_key": "priv-1", "public_key": "pub-1"})
        events.create({"classroom_id": room_id, "sensor_id": "s-1", "event_time": datetime.utcnow()})

        service = RoomsService(None, rooms, events, sensors)
        deleted = service.delete_room_by_id(room_id)

        self.assertTrue(deleted)
        self.assertIsNone(rooms.get_by_id(room_id))
        self.assertEqual(len(sensors.list_by_room_id(room_id)), 0)

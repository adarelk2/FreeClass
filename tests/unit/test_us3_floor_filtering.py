import unittest

from core.infrastructure.mock_json_db import MockJSONDB
from repositories.classrooms_repository_mock import ClassroomsRepositoryMock


class TestUS3FloorFiltering(unittest.TestCase):
    def test_floor_filtering(self):
        rooms = ClassroomsRepositoryMock(MockJSONDB())

        building_id = 1
        rooms.create({"id_building": building_id, "floor": 1, "class_number": 10, "category": 1})
        rooms.create({"id_building": building_id, "floor": 2, "class_number": 20, "category": 1})

        floor_2_rooms = rooms.list_by_floor(building_id, 2)

        self.assertEqual(len(floor_2_rooms), 1)
        self.assertEqual(floor_2_rooms[0].class_number, 20)

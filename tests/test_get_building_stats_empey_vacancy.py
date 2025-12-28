import unittest
from unittest.mock import MagicMock
from services.building_service import BuildingService

class TestBuildingService(unittest.TestCase):
    def setUp(self):
        # Mock the database and models
        self.mock_db = MagicMock()
        self.mock_building_model = MagicMock()
        self.mock_classrooms_model = MagicMock()
        self.mock_rooms_service = MagicMock()
        
        self.service = BuildingService(
            db_instance=self.mock_db,
            building_model=self.mock_building_model,
            classrooms_model=self.mock_classrooms_model,
            rooms_service=self.mock_rooms_service
        )

    def test_get_building_stats_empty_vacancy(self):
        """
        US#2.4: Verify that the service returns a '0' availability 
        count correctly when no rooms in the building are available.
        """
        # GIVEN: A building (ID 1) and two rooms belonging to it
        self.mock_building_model.filter.return_id = [{"id": 1, "name": "Engineering Building"}]
        self.mock_classrooms_model.filter.return_value = [
            {"id": 101, "id_building": 1, "name": "Room 1"},
            {"id": 102, "id_building": 1, "name": "Room 2"}
        ]
        
        # AND: The rooms_service reports ZERO available room IDs
        self.mock_rooms_service.getAvailableRoomIds.return_value = []

        # WHEN: We fetch stats for building 1
        result = self.service.get_buildings_with_rooms(building_ids=[1], include_availability=True)

        # THEN: The building should be found
        self.assertEqual(len(result), 1)
        # AND: All rooms must explicitly show 'is_available' as False (not None or Error)
        for room in result[0]["rooms"]:
            self.assertFalse(room["is_available"], f"Room {room['id']} should be unavailable.")
# tests/test_building_model_simple.py
import unittest

from core.database import db
from models.building_model import BuildingModel


class TestBuildingModelSimple(unittest.TestCase):
    def test_create_and_get_by_id(self):
        model = BuildingModel(db)

        # 1) create
        new_id = model.create({
            "building_name": "test-building",
            "floors": 4,
        })

        # 2) basic checks on id
        self.assertIsInstance(new_id, int)
        self.assertGreater(new_id, 0)

        # 3) get_by_id and verify row
        row = model.get_by_id(new_id)
        self.assertIsNotNone(row)
        self.assertEqual(row["id"], new_id)
        self.assertEqual(row["building_name"], "test-building")
        self.assertEqual(row["floors"], 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)

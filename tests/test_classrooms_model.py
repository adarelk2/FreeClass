# tests/test_classrooms_model.py
import unittest
import random

from core.database import db
from models.class_rooms_model import ClassRoomsModel


class TestClassRoomsModelSimple(unittest.TestCase):
    def test_create_and_get_by_id(self):
        model = ClassRoomsModel(db)

        # choose unique class_number to avoid uq_classroom_location collision
        class_number = random.randint(10000, 99999)

        new_id = model.create({
            "id_building": 1,   # חייב להיות קיים
            "floor": 1,
            "class_number": class_number,
        })

        self.assertIsInstance(new_id, int)
        self.assertGreater(new_id, 0)

        row = model.get_by_id(new_id)
        self.assertIsNotNone(row)

        self.assertEqual(row["id"], new_id)
        self.assertEqual(row["id_building"], 1)
        self.assertEqual(row["floor"], 1)
        self.assertEqual(row["class_number"], class_number)


if __name__ == "__main__":
    unittest.main(verbosity=2)

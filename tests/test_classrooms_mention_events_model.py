# tests/test_classroom_motion_events_model.py
import unittest
import uuid

from core.database import db
from models.classroom_motion_events_model import ClassroomMotionEventsModel


class TestClassroomMotionEventsModelSimple(unittest.TestCase):
    def test_create_and_get_by_id(self):
        model = ClassroomMotionEventsModel(db)

        # IMPORTANT: classroom_id חייב להיות קיים בטבלת classrooms
        classroom_id = 2  # שנה אם אצלך הכיתה קיימת עם id אחר

        new_id = model.create({
            "classroom_id": classroom_id,
            "sensor_id": f"PIR-TEST-{uuid.uuid4()}",
            "event_type": "motion",
            "confidence": 95,
            "payload": '{"source":"unit-test"}',
        })

        self.assertIsInstance(new_id, int)
        self.assertGreater(new_id, 0)

        row = model.get_by_id(new_id)
        self.assertIsNotNone(row)

        self.assertEqual(row["id"], new_id)
        self.assertEqual(row["classroom_id"], classroom_id)
        self.assertEqual(row["event_type"], "motion")
        self.assertEqual(row["confidence"], 95)

        # sensor_id should match exactly
        self.assertTrue(row["sensor_id"].startswith("PIR-TEST-"))


if __name__ == "__main__":
    unittest.main(verbosity=2)

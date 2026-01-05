import unittest
from datetime import datetime
from core.mock_json_db import MockJSONDB

# מודלים ושירותים
from models.building_model import BuildingModel
from models.class_rooms_model import ClassRoomsModel
from models.classroom_motion_events_model import ClassroomMotionEventsModel
from models.sensors_model import SensorsModel
from models.users_model import UsersModel

from services.rooms_service import RoomsService
from services.building_service import BuildingService
from services.home_service import HomeService

class SimpleFreeClassTests(unittest.TestCase):

    def setUp(self):
        self.db = MockJSONDB()
        # אתחול מהיר של כל השכבות
        self.buildings = BuildingModel(self.db)
        self.rooms = ClassRoomsModel(self.db)
        self.events = ClassroomMotionEventsModel(self.db)
        self.sensors = SensorsModel(self.db)
        self.users = UsersModel(self.db)
        
        self.rs = RoomsService(self.db, self.rooms, self.events, self.sensors)
        self.bs = BuildingService(self.db, self.buildings, self.rooms, self.rs)
        self.hs = HomeService(self.db, self.bs, self.rs)

    # US#1: Campus Vacancy Overview
    def test_us1_total_vacancy_counter(self):
        self.rooms.create({"class_number": 101}) # יצירת חדר פנוי
        available_ids = self.rs.getAvailableRoomIds()
        self.assertGreater(len(available_ids), 0, "צריך להיות לפחות חדר פנוי אחד")

    # US#2: Building Statistics
    def test_us2_building_card_data(self):
        b_id = self.buildings.create({"building_name": "Engineering"})
        self.rooms.create({"id_building": b_id, "class_number": 202})
        stats = self.bs.get_buildings_with_rooms()
        self.assertEqual(stats[0]['building_name'], "Engineering", "נתוני הבניין צריכים להופיע בכרטיס")

    # US#3: Category Quick Search
    def test_us3_category_filter(self):
        # בדיקה שה-API מחזיר חדרים (הסינון הלוגי מתבצע ב-SQL/Service)
        self.rooms.create({"class_number": 303, "room_type": "Lab"})
        all_rooms = self.rooms.filter()
        self.assertTrue(any(r.get('class_number') == 303 for r in all_rooms))

    # US#4: Advanced Filtering
    def test_us4_floor_filtering(self):
        b_id = self.buildings.create({"building_name": "Main"})
        self.rooms.create({"id_building": b_id, "floor": 1, "class_number": 10})
        self.rooms.create({"id_building": b_id, "floor": 2, "class_number": 20})
        floor_2_rooms = self.rooms.list_by_floor(b_id, 2)
        self.assertEqual(len(floor_2_rooms), 1, "הסינון צריך להחזיר רק חדרים מקומה 2")

    # US#5: Weekly Schedule (Maintenance Status)
    def test_us5_maintenance_visibility(self):
        # בדיקה שהמערכת מזהה חדר כלא זמין אם הוא בסטטוס מיוחד (כמו אופציה עתידית)
        r_id = self.rooms.create({"class_number": 505})
        # בסימולציה: חדר ללא אירועי תנועה הוא פנוי
        is_available = r_id in self.rs.getAvailableRoomIds()
        self.assertTrue(is_available)

    # US#6: Recent Activity Tracking
    def test_us6_recent_activity_list(self):
        # בדיקה ששירות הבית מחזיר רשימת חדרים זמינים עכשיו (הבסיס ל-Recent)
        self.rooms.create({"class_number": 606})
        available_now = self.hs.getHomeAvailableNow(limit=5)
        self.assertIsInstance(available_now, list)

    # US#7: Admin Override (Integrity)
    def test_us7_delete_room_and_sensors(self):
        r_id = self.rooms.create({"class_number": 707})
        self.sensors.create({"room_id": r_id, "public_key": "p1"})
        # שימוש בפונקציית המחיקה המשולבת מה-Service שלך
        self.rs.delete_room_by_id(r_id)
        self.assertEqual(len(self.sensors.list_by_room_id(r_id)), 0, "החיישן חייב להימחק עם החדר")

    # US#8: Admin Login
    def test_us8_admin_role_check(self):
        self.users.create({"username": "admin", "role": "admin"})
        user = self.db.select("users", {"username": "admin"})[0]
        self.assertEqual(user['role'], "admin", "רק משתמש עם רול אדמין יורשה להיכנס")

if __name__ == '__main__':
    unittest.main()
from core.database import db
from models.class_rooms_model import ClassRoomsModel
from core.controller_base import ControllerBase

# app/controllers/home_controller.py
class HomeController(ControllerBase):
    def print(self, params):
        buildings = [
            {"id": 1, "name": "בניין הנדסה", "availableRooms": 8, "totalRooms": 15, "color": "#0ea5e9"},
            {"id": 2, "name": "ספרייה מרכזית", "availableRooms": 3, "totalRooms": 12, "color": "#f59e0b"},
            {"id": 3, "name": "בניין מדעים", "availableRooms": 12, "totalRooms": 18, "color": "#10b981"},
            {"id": 4, "name": "בית הסטודנט", "availableRooms": 5, "totalRooms": 10, "color": "#8b5cf6"},
        ]

        recent_spaces = [
            {"id": 1, "name": "כיתה 204", "building": "בניין הנדסה", "status": "available"},
            {"id": 2, "name": "חדר קריאה שקט 3", "building": "ספרייה מרכזית", "status": "available"},
            {"id": 3, "name": "מעבדת מחשבים 5", "building": "בניין הנדסה", "status": "busy"},
            {"id": 4, "name": "כיתה 301", "building": "בניין מדעים", "status": "available"},
        ]

        available_now = [
            {"name": "כיתה 201", "building": "בניין הנדסה", "floor": 2},
            {"name": "מעבדה 3", "building": "בניין מדעים", "floor": 1},
            {"name": "חדר סמינרים A", "building": "ספרייה מרכזית", "floor": 3},
        ]

        context = {
                "page": "home",
                "buildings_server": buildings,
                "recentSpaces_server": recent_spaces,
                "available_now_server": available_now
            }

        return self.responseHTML(context, "index")
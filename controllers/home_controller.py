# app/controllers/home_controller.py
class HomeController:
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

        return {
            "template": "pages/index.html",
            "context": {
                "page": "home",
                "buildings_server": buildings,
                "recentSpaces_server": recent_spaces,
                "available_now_server": available_now
            },
            "status": 200,
        }

    def makeLogin(self, params):
        return {
            "json": {
                "totalBuildings": 4,
                "totalRooms": 55,
                "availableRooms": 28
            },
            "status": 200
        }
         
    def index(self, params):
        return self.print(params)

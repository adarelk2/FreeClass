from core.database import db
from models.sensors_model import SensorsModel
from models.building_model import BuildingModel
from models.class_rooms_model import ClassRoomsModel
from models.classroom_motion_events_model import ClassroomMotionEventsModel

# app/controllers/home_controller.py
class DashboardadminController:
    def print(self, params):
        return {
                "template": "pages/admin-dashboard.html",
                "context": {
                    "page": "home",
                    },
                "status": 200,
                }

    def createNewActivty(self, params):
        sensor_model = SensorsModel(db)
        sensor_token = params.get("token", "token")
        sensor = sensor_model.get_by_token(sensor_token)

        if sensor:
            mention_events_model = ClassroomMotionEventsModel(db)
            new_row = {"classroom_id":sensor['room_id'], "sensor_id": sensor['id']}
            id = mention_events_model.create(new_row)
            return {"json": {"flag":True, "id":id}}

        return {"json": {"flag":False}}

    def createNewSensor(self, params):
        #make auth for admin important!
        sensor_model = SensorsModel(db)
        sensor_token = params.get("token", "")
        room_id = params.get("room_id", "")

        classRoom_model = ClassRoomsModel(db)

        room = classRoom_model.get_by_id(room_id)
        if room:
            id = sensor_model.create({"room_id":room_id, "token" : sensor_token})
            return {"json": {"flag":True, "id":id}}

        return {"json": {"flag":False}}

    def createNewRoom(self, params):
        #make auth for admin important!
        building_id = params.get("building_id", "")
        floor = params.get("floor", 0)
        class_number = params.get("class_number", 0)
        building_model = BuildingModel(db)

        building = building_model.get_by_id(building_id)
        if building:
            room_model = ClassRoomsModel(db)

            id = room_model.create({"id_building":building_id, "floor":floor, "class_number": class_number})
            return {"json": {"flag":True, "id":id}}

        return {"json": {"flag":False}}

    def createNewBuilding(self, params):
        #make auth for admin important!
        building_name = params.get("building_name", "")
        floors= params.get("floors", 0)
        building_model = BuildingModel(db)

        id = building_model.create({"building_name": building_name, "floors": floors})
        if id:
            return {"json": {"flag":True, "id":id}}

        return {"json": {"flag":False}}
from core.database import db
from models.sensors_model import SensorsModel
from models.building_model import BuildingModel
from models.class_rooms_model import ClassRoomsModel
from models.classroom_motion_events_model import ClassroomMotionEventsModel
from models.class_room_categories import ClassRoomCategoriesModel
from core.controller_base import ControllerBase
from core.config import (SECRET_JWT_KEY)
from services.home_service import HomeService
from services.rooms_service import RoomsService

import jwt


# app/controllers/home_controller.py
class DashboardadminController(ControllerBase):
    def print(self, params):
        service = HomeService()
    
        sensor_model = SensorsModel(db)
        rooms_model = ClassRoomsModel(db)
        class_room_categories_model = ClassRoomCategoriesModel(db)
        categories = class_room_categories_model.filter()
        rooms = rooms_model.filter()
        buildings = service.getHomeBuildingsCards()
        context = {
            "buildings_server": buildings,
            "classRoom_categories_server" : categories,
            "rooms_server": rooms,
            "sensors_server": sensor_model.filter()
        }
        return self.responseHTML(context, "admin-dashboard")

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
        category_id = params.get("category_id", 0)

        building_model = BuildingModel(db)

        building = building_model.get_by_id(building_id)
        if building:
            room_model = ClassRoomsModel(db)

            id = room_model.create({"id_building":building_id, "floor":floor, "class_number": class_number, "category": category_id})
            return {"json": {"flag":True, "id":id}}

        return {"json": {"flag":False}}

    def createNewBuilding(self, params):
        #make auth for admin important!
        building_name = params.get("building_name", "")
        floors= params.get("floors", 0)
        color= params.get("color", "#000")
        building_model = BuildingModel(db)

        id = building_model.create({"building_name": building_name, "floors": floors, "color": color})
        if id:
            return {"json": {"flag":True, "id":id}}

        return {"json": {"flag":False}}

    def authToken(self, params):
        context = {}
        flag = False

        try:
            token = jwt.decode(
                params["token"],
                SECRET_JWT_KEY,
                algorithms=["HS256"]
            )

            flag = True

        except jwt.ExpiredSignatureError:
            context["error"] = "Token expired"

        except jwt.InvalidTokenError:
            context["error"] = "Invalid token"

        return self.responseJSON(context, flag)
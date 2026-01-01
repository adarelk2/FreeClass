from core.controller_base import ControllerBase
from core.config import (SECRET_JWT_KEY)
from core.validations.CreateValidation import CreateValidation
from container import createModel
from container import createService
import jwt
import time
# app/controllers/home_controller.py
class DashboardadminController(ControllerBase):
    def print(self, params):
        service = createService("HomeService")
    
        sensor_model = createModel("SensorsModel")
        class_rooms_model = createModel("ClassRoomsModel")
        class_room_categories_model = createModel("ClassRoomCategoriesModel")
        categories = class_room_categories_model.filter()
        rooms = class_rooms_model.filter()
        buildings = service.getHomeBuildingsCards()
        context = {
            "buildings_server": buildings,
            "classRoom_categories_server" : categories,
            "rooms_server": rooms,
            "sensors_server": list(map(lambda s: {"id": s['id'], "room_id" : s['room_id'], 'public_key': s['public_key']}, sensor_model.filter()))
        }
        return self.responseHTML(context, "admin-dashboard")

    def createNewActivty(self, params):
        sensor_model = createModel("SensorsModel")
        sensor_private_key = params.get("private_key", "private_key")
        sensor = sensor_model.get_by_privateKey(sensor_private_key)

        if sensor:
            mention_events_model = createModel("ClassroomMotionEventsModel")
            new_row = {"classroom_id":sensor['room_id'], "sensor_id": sensor['id']}
            id = mention_events_model.create(new_row)
            return {"json": {"flag":True, "id":id}}

        return {"json": {"flag":False}}

    def createNewSensor(self, params):    
        validator = CreateValidation("sensor", params).create_validator()
        errors = validator.validate()
        if errors:
           return self.responseJSON(errors, False)
        #make auth for admin important!
        sensor_model = createModel("SensorsModel")

        private_key = jwt.encode({"role": "private_key", "iat": int(time.time())}, SECRET_JWT_KEY, algorithm="HS256")

        room_id = params.get("room_id", "")
        classRoom_model = createModel("ClassRoomsModel")
        room = classRoom_model.get_by_id(room_id)
        if room:
            id = sensor_model.create({"room_id":room_id, "private_key" : private_key, "public_key" : params['public_key']})
            return self.responseJSON({"public_key": params['public_key'], "private_key": private_key, "id": id}, True)
        
        return self.responseJSON({}, False)
    
    def createNewRoom(self, params):
        validator = CreateValidation("room", params).create_validator()
        errors = validator.validate()
        if errors:
           return self.responseJSON(errors, False)
        #make auth for admin important!
        building_id = params.get("building_id", "")
        floor = params.get("floor", 0)
        class_number = params.get("class_number", 0)
        category_id = params.get("category_id", 0)


        building_model = createModel("BuildingModel")

        building = building_model.get_by_id(building_id)
        if building:
            room_model = createModel("ClassRoomsModel")

            id = room_model.create({"id_building":building_id, "floor":floor, "class_number": class_number, "category": category_id})
            return self.responseJSON({"id":id}, True)

        return self.responseJSON({}, False)

    def createNewBuilding(self, params):
        validator = CreateValidation("building", params).create_validator()
        errors = validator.validate()
        flag = False
        context = {}
        if errors:
           return self.responseJSON(errors, flag)
        #make auth for admin important!
        building_name = params.get("building_name", "")
        floors= params.get("floors", 0)
        color= params.get("color", "#000")
        building_model = createModel("BuildingModel")

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

    def deleteClassRoom(self, params):
        context = {}
        flag = False
        class_id = params["class_id"]
        class_model = createModel("ClassRoomsModel")
        check_room = class_model.get_by_id(class_id)
        if check_room:
            flag = True
            room_service = createService("RoomsService")
            room_service.delete_room_by_id(class_id)

        return self.responseJSON(context, flag)
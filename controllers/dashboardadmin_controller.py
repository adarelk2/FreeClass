from core.controller_base import ControllerBase
from core.config import (SECRET_JWT_KEY)
from core.validations.CreateValidation import CreateValidation
import jwt
import time
# app/controllers/home_controller.py
class DashboardadminController(ControllerBase):
    def __init__(self, _container):
        #models
        self.sensor_model = _container.sensors_model
        self.class_rooms_model = _container.class_rooms_model
        self.class_room_categories_model = _container.categories_model
        self.motion_events_model = _container.motion_events_model
        self.building_model = _container.building_model

        ##Services
        self.home_service = _container.home_service
        self.rooms_service = _container.rooms_service
        self.building_service = _container.building_service

    def print(self, params):
        categories = self.class_room_categories_model.filter()
        rooms = self.class_rooms_model.filter()
        buildings = self.home_service.getHomeBuildingsCards()
        context = {
            "buildings_server": buildings,
            "classRoom_categories_server" : categories,
            "rooms_server": rooms,
            "sensors_server": list(map(lambda s: {"id": s['id'], "room_id" : s['room_id'], 'public_key': s['public_key']}, self.sensor_model.filter()))
        }

        return self.responseHTML(context, "admin-dashboard")

    def createNewActivty(self, params):
        sensor_private_key = params.get("private_key", "private_key")
        sensor = self.sensor_model.get_by_privateKey(sensor_private_key)

        if sensor:
            new_row = {"classroom_id":sensor['room_id'], "sensor_id": sensor['id']}
            self.motion_events_model.create(new_row)
            return self.responseJSON("Done", True)

        return self.responseJSON("Error - sensor not found", False)

    def createNewSensor(self, params):    
        validator = CreateValidation("sensor", params).create_validator()
        errors = validator.validate()
        if errors:
           return self.responseJSON(errors, False)
        #make auth for admin important!
        private_key = jwt.encode({"role": "private_key", "iat": int(time.time())}, SECRET_JWT_KEY, algorithm="HS256")

        room_id = params.get("room_id", "")

        room = self.class_rooms_model.get_by_id(room_id)
        if room:
            id = self.sensor_model.create({"room_id":room_id, "private_key" : private_key, "public_key" : params['public_key']})
            return self.responseJSON({"public_key": params['public_key'], "private_key": private_key, "id": id}, True)

        return self.responseJSON("Error - room not found", False)

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

        building = self.building_model.get_by_id(building_id)
        if building:
            id = self.class_rooms_model.create({"id_building":building_id, "floor":floor, "class_number": class_number, "category": category_id})
            return self.responseJSON({"id":id}, True)

        return self.responseJSON("Error - building not found", False)

    def createNewBuilding(self, params):
        validator = CreateValidation("building", params).create_validator()
        errors = validator.validate()
        if errors:
           return self.responseJSON(errors, False)
        #make auth for admin important!
        building_name = params.get("building_name", "")
        floors= params.get("floors", 0)
        color= params.get("color", "#000")

        id = self.building_model.create({"building_name": building_name, "floors": floors, "color": color})
        if id:
            return self.responseJSON({"id":id}, True)   

        return self.responseJSON("Error", False)

    def authToken(self, params):##For future use
        context = {}
        flag = False

        try:
            jwt.decode(
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
        class_id = params["class_id"]
        if self.rooms_service.delete_room_by_id(class_id):
            return self.responseJSON("Done", True)

        return self.responseJSON("Error - Operation failed", False)


    def deleteBuilding(self, params):
        building_id = params["building_id"]
        if self.building_service.delete_building_by_id(building_id):
            return self.responseJSON("Done", True)

        return self.responseJSON("Error - building not found", False)
from core.controller_base import ControllerBase
from core.config import (SECRET_JWT_KEY)
from core.validations.CreateValidation import CreateValidation
import jwt
import time

class DashboardadminController(ControllerBase):
    def __init__(self, _container):
        # Services only - no direct model access
        self.home_service = _container.home_service
        self.rooms_service = _container.rooms_service
        self.building_service = _container.building_service
        self.sensors_service = _container.sensors_service
        self.categories_service = _container.categories_service
        self.motion_events_service = _container.motion_events_service

    def print(self, params):
        categories = self.categories_service.list_all()
        rooms = self.rooms_service.list_all()
        buildings = self.home_service.getHomeBuildingsCards()
        context = {
            "buildings_server": buildings,
            "classRoom_categories_server" : categories,
            "rooms_server": rooms,
            "sensors_server": list(map(lambda s: {"id": s['id'], "room_id" : s['room_id'], 'public_key': s['public_key']}, self.sensors_service.list_all()))
        }

        return self.responseHTML(context, "admin-dashboard")

    def createNewActivty(self, params):
        sensor_private_key = params.get("private_key", "private_key")
        
        if self.motion_events_service.log_sensor_activity(sensor_private_key):
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

        sensor_id = self.sensors_service.create_sensor(room_id, private_key, params['public_key'])
        if sensor_id:
            return self.responseJSON({"public_key": params['public_key'], "private_key": private_key, "id": sensor_id}, True)

        return self.responseJSON("Error - room not found", False)

    def createNewRoom(self, params):
        validator = CreateValidation("room", params).create_validator()
        errors = validator.validate()
        if errors:
           return self.responseJSON(errors, False)
        
        building_id = params.get("building_id", "")
        floor = params.get("floor", 0)
        class_number = params.get("class_number", 0)
        category_id = params.get("category_id", 0)

        building = self.building_service.get_building_by_id(building_id)
        if building:
            room_id = self.rooms_service.create_room(building_id, floor, class_number, category_id)
            return self.responseJSON({"id": room_id}, True)

        return self.responseJSON("Error - building not found", False)

    def createNewBuilding(self, params):
        validator = CreateValidation("building", params).create_validator()
        errors = validator.validate()
        if errors:
           return self.responseJSON(errors, False)
        
        building_name = params.get("building_name", "")
        floors = params.get("floors", 0)
        color = params.get("color", "#000")

        building_id = self.building_service.create_building(building_name, floors, color)
        if building_id:
            return self.responseJSON({"id": building_id}, True)   

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

    def deleteSensor(self, params):
        sensor_id = params.get("sensor_id")
        if not sensor_id:
            return self.responseJSON("Error - missing sensor_id", False)

        try:
            sid = int(sensor_id)
        except (TypeError, ValueError):
            return self.responseJSON("Error - invalid sensor_id", False)

        # Use repository delete through the service's repository
        # Delegate deletion to service layer
        if self.sensors_service.delete_sensor(sid):
            return self.responseJSON("Done", True)

        return self.responseJSON("Error - sensor not found", False)
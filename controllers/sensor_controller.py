from core.database import db
from models.sensors_model import SensorsModel
from models.class_rooms_model import ClassRoomsModel
from models.classroom_motion_events_model import ClassroomMotionEventsModel

# app/controllers/home_controller.py
class SensorController:
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
            print(sensor_token)
            id = sensor_model.create({"room_id":room_id, "token" : sensor_token})
            return {"json": {"flag":True, "id":id}}

        return {"json": {"flag":False}}
# db
from core.database import db

# models
from models.building_model import BuildingModel
from models.class_room_categories import ClassRoomCategoriesModel
from models.class_rooms_model import ClassRoomsModel
from models.classroom_motion_events_model import ClassroomMotionEventsModel
from models.sensors_model import SensorsModel
from models.users_model import UsersModel

# services
from services.rooms_service import RoomsService
from services.building_service import BuildingService
from services.home_service import HomeService

# to do list fix duplicate
def createService(_service):
    if _service == "RoomsService":
        return  RoomsService(db ,createModel("ClassRoomsModel") ,createModel("ClassroomMotionEventsModel") ,createModel("SensorsModel"))
    elif _service == "BuildingService":
        return BuildingService(db ,createModel("BuildingModel") ,createModel("ClassRoomsModel") ,createService("RoomsService"))
    elif _service  == "HomeService":
        return HomeService(db, createService("BuildingService"), createService("RoomsService"), createModel("BuildingModel") ,createModel("ClassRoomsModel") ,createModel("ClassroomMotionEventsModel")  )
    else:
        return None

def createModel(_model):
    if _model == "BuildingModel":
        return BuildingModel(db)
    elif _model == "ClassRoomCategoriesModel":
        return ClassRoomCategoriesModel(db)
    elif _model == "ClassRoomsModel":
        return ClassRoomsModel(db)
    elif _model == "ClassroomMotionEventsModel":
        return ClassroomMotionEventsModel(db)
    elif _model == "SensorsModel":
        return SensorsModel(db)
    elif _model == "UsersModel":
        return UsersModel(db)
    else:
        return None
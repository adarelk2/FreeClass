# controllers/home_controller.py
from core.database import db
from core.controller_base import ControllerBase
from services.building_service import BuildingService
from models.class_room_categories import ClassRoomCategoriesModel

class SearchController(ControllerBase):
    def print(self, params):
        building_service = BuildingService()
        class_room_categoiry_model = ClassRoomCategoriesModel(db)
        buildings = building_service.get_buildings_with_rooms()
        context = {
            "page": "search",
            "buildings" : buildings,
            "categories_server" : class_room_categoiry_model.filter()
        }

        return self.responseHTML(context, "search")

# controllers/home_controller.py
from core.controller_base import ControllerBase
from container import createModel
from container import createService

class SearchController(ControllerBase):
    def print(self, params):
        building_service = createService("BuildingService")
        class_room_categories_model = createModel("ClassRoomCategoriesModel")
        buildings = building_service.get_buildings_with_rooms()
        context = {
            "page": "search",
            "buildings" : buildings,
            "categories_server" : class_room_categories_model.filter()
        }

        return self.responseHTML(context, "search")

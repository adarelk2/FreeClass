# controllers/home_controller.py
from core.controller_base import ControllerBase

class SearchController(ControllerBase):
    def __init__(self, _container):
        self.building_service = _container.building_service

        self.class_room_categories_model = _container.categories_model

    def print(self, params):
        buildings = self.building_service.get_buildings_with_rooms()
        context = {
            "page": "search",
            "buildings" : buildings,
            "categories_server" : self.class_room_categories_model.filter()
        }

        return self.responseHTML(context, "search")

# controllers/home_controller.py
from core.controller_base import ControllerBase

class SearchController(ControllerBase):
    def __init__(self, _container):
        self.building_service = _container.building_service
        self.categories_service = _container.categories_service

    def print(self, params):
        buildings = self.building_service.get_buildings_with_rooms()
        
        context = {
            "page": "search",
            "buildings" : buildings,
            "categories_server" : self.categories_service.list_all()
        }

        return self.responseHTML(context, "search")

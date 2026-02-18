# controllers/search_controller.py
from core.controller_base import ControllerBase

class SearchController(ControllerBase):
    def __init__(self, _container):
        self.building_service = _container.building_service
        self.categories_service = _container.categories_service

    def print(self, params):
        # Always get availability status for accurate room display
        buildings = self.building_service.get_buildings_with_rooms(include_availability=True)
        categories = self.categories_service.list_all()
        
        context = {
            "page": "search",
            "buildings" : buildings,
            "categories_server" : categories
        }

        return self.responseHTML(context, "search")

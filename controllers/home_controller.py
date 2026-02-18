# controllers/home_controller.py
from core.controller_base import ControllerBase

class HomeController(ControllerBase):
    def __init__(self, _container):
        self.home_service = _container.home_service
        
    def print(self, params):
        # Fetch all data once to avoid duplicate queries
        cached_data = self.home_service._prepare_home_data()
        
        # Use cached data for all three methods
        buildings = self.home_service.getHomeBuildingsCards(cached_data=cached_data)
        recent_spaces = self.home_service.getHomeRecentSpaces(limit=10, cached_data=cached_data)
        available_now = self.home_service.getHomeAvailableNow(limit=6, cached_data=cached_data)

        context = {
            "page": "home",
            "buildings_server": buildings,
            "recentSpaces_server": recent_spaces,
            "available_now_server": available_now,
        }

        return self.responseHTML(context, "index")

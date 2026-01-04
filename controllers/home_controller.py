# controllers/home_controller.py
from core.controller_base import ControllerBase

class HomeController(ControllerBase):
    def __init__(self, _container):
        self.home_service = _container.home_service
        
    def print(self, params):

        buildings = self.home_service.getHomeBuildingsCards()
        recent_spaces = self.home_service.getHomeRecentSpaces(limit=10)
        available_now = self.home_service.getHomeAvailableNow(limit=6)

        context = {
            "page": "home",
            "buildings_server": buildings,
            "recentSpaces_server": recent_spaces,
            "available_now_server": available_now,
        }

        return self.responseHTML(context, "index")

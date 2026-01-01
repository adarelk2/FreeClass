# controllers/home_controller.py
from core.controller_base import ControllerBase
from container import createModel
from container import createService

class HomeController(ControllerBase):
    def print(self, params):
        service = createService("HomeService")

        buildings = service.getHomeBuildingsCards()
        recent_spaces = service.getHomeRecentSpaces(limit=10)
        available_now = service.getHomeAvailableNow(limit=6)

        context = {
            "page": "home",
            "buildings_server": buildings,
            "recentSpaces_server": recent_spaces,
            "available_now_server": available_now,
        }

        return self.responseHTML(context, "index")

# controllers/home_controller.py
from core.controller_base import ControllerBase
from services.dashboard_service import DashboardService


class SearchController(ControllerBase):
    def print(self, params):
       
        
        context = {
            "page": "search",
          
        }

        return self.responseHTML(context, "search")

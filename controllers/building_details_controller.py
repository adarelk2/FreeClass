from core.controller_base import ControllerBase
from services.dashboard_service import DashboardService

from core.database import db

class Building_detailsController(ControllerBase):
    def print(self, params):
        id = params["id"]

        service = DashboardService()
        building_by_service = service.getBuildingWithRoomsById(id)

        context = {"building": building_by_service}
        return self.responseHTML(context, "building-details")
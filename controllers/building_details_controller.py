from core.controller_base import ControllerBase
from services.building_service import BuildingService
from core.database import db

class Building_detailsController(ControllerBase):
    def print(self, params):
        id = params["id"]

        service = BuildingService()
        building_by_service = service.get_buildings_with_rooms([id])[0]
        print(building_by_service)
        context = {"building": building_by_service}
        return self.responseHTML(context, "building-details")
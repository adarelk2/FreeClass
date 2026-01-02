from core.controller_base import ControllerBase
from container import createModel
from container import createService

class Building_detailsController(ControllerBase):
    def print(self, params):
        id = params["id"]
        service = createService("BuildingService")
        building_by_service = service.get_buildings_with_rooms([id])[0]
        context = {"building": building_by_service}
        return self.responseHTML(context, "building-details")
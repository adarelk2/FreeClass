from core.controller_base import ControllerBase

class Building_detailsController(ControllerBase):
    def __init__(self, _container):
        self.building_service = _container.building_service
        
    def print(self, params):
        id = params["id"]
        building_by_service = self.building_service.get_buildings_with_rooms([id])[0]
        context = {"building": building_by_service}
        return self.responseHTML(context, "building-details")
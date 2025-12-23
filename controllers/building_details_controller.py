from core.controller_base import ControllerBase
from models.building_model import BuildingModel
from core.database import db

class Building_detailsController(ControllerBase):
    def print(self, params):
        building_model = BuildingModel(db)
        id = params["id"]
        building = building_model.get_by_id(id)
        print(building)


        context = {"building": building}
        return self.responseHTML(context, "building-details")
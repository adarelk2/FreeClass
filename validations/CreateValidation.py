from validations.SensorValidation import SensorValidation
from validations.RoomValidation import RoomValidation
from validations.BuildingValidation import BuildingValidation


class CreateValidation:
    def __init__(self, str, params):
        self.params = params
        self.str = str

    def create_validator(self):
        if self.str == "sensor":
            return SensorValidation(self.params)
        if self.str == "room":
            return RoomValidation(self.params)
        if self.str == "building":
            return BuildingValidation(self.params)

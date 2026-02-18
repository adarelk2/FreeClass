from validations.validation import ValidationInterface


class BuildingValidation(ValidationInterface):
    """ולידטור עבור מבנים."""

    def validate(self):
        self.errors = []
        data = self.params

        name = data.get("building_name", "")
        if not isinstance(name, str) or not name.strip():
            self.errors.append("Name is required and must be a non-empty string.")

        floors = data.get("floors", None)
        if floors is None or not isinstance(floors, int) or floors <= 0:
            self.errors.append("Floors is required and must be a positive integer.")

        color = data.get("color", "")
        if not isinstance(color, str) or not color.strip():
            self.errors.append("Color is required and must be a non-empty string.")

        return self.errors

from core.validations.validation import ValidationInterface
class BuildingValidation(ValidationInterface):
    """ולידטור עבור מבנים."""

    def validate(self):
        self.errors = []
        data = self.params

        # בדיקה אם name קיים והוא מחרוזת לא ריקה
        name = data.get("building_name", "")
        if not isinstance(name, str) or not name.strip():
            self.errors.append("Name is required and must be a non-empty string.")
        # בדיקה אם floors קיים והוא מספר שלם חיובי
        floors = data.get("floors", None)
        if floors is None or not isinstance(floors, int) or floors <= 0:
            self.errors.append("Floors is required and must be a positive integer.")
        # בדיקה אם color קיים והוא מחרוזת לא ריקה
        color = data.get("color", "")
        if not isinstance(color, str) or not color.strip():
            self.errors.append("Color is required and must be a non-empty string.")

        return self.errors
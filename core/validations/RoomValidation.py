from core.validations.validation import ValidationInterface

class RoomValidation(ValidationInterface):
    """ולידטור עבור חדרים."""

    def validate(self):
        self.errors = []
        data = self.params


        category_id = data.get("category_id", None)
        if category_id is None or not isinstance(category_id, int) or category_id <= 0:
            self.errors.append("Category ID is required and must be a positive integer.")

        # בדיקה אם building_id קיים והוא מספר שלם חיובי
        building_id = data.get("building_id", None)
        if building_id is None or not isinstance(building_id, int) or building_id <= 0:
            self.errors.append("Building ID is required and must be a positive integer.")

        # בדיקה אם floor קיים והוא מספר שלם (יכול להיות שלילי)
        floor = data.get("floor", None)
        if floor is None or not isinstance(floor, int):
            self.errors.append("Floor is required and must be an integer.")

        # בדיקה אם class_number קיים והוא מספר שלם חיובי
        class_number = data.get("class_number", None)
        if class_number is None or not isinstance(class_number, int) or class_number <= 0:
            self.errors.append("Class number is required and must be a positive integer.")

        return self.errors
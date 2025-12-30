from core.validations.validation import ValidationInterface

class SensorValidation(ValidationInterface):
    """ולידטור עבור חיישנים."""

    def validate(self):
        self.errors = []
        data = self.params
        # בדיקה אם הטוקן קיים והוא מחרוזת לא ריקה
        public_key = data.get("public_key", "")
        if not isinstance(public_key, str) or not public_key.strip():
            self.errors.append("public Key is required and must be a non-empty string.")

        # # בדיקה אם הטוקן קיים והוא מחרוזת לא ריקה
        # public_key = data.get("public_key", "")
        # if not isinstance(public_key, str) or not public_key.strip():
        #     self.errors.append("Public Key is required and must be a non-empty string.")
        
        # בדיקה אם room_id קיים והוא מספר שלם חיובי
        room_id = data.get("room_id", None)
        if room_id is None or not isinstance(room_id, int) or room_id <= 0:
            self.errors.append("Room ID is required and must be a positive integer.")

        return self.errors
# container.py
from __future__ import annotations
from typing import Optional

# db
from core.database import db

# models
from models.building_model import BuildingModel
from models.class_room_categories import ClassRoomCategoriesModel
from models.class_rooms_model import ClassRoomsModel
from models.classroom_motion_events_model import ClassroomMotionEventsModel
from models.sensors_model import SensorsModel
from models.users_model import UsersModel

# services
from services.rooms_service import RoomsService
from services.building_service import BuildingService
from services.home_service import HomeService


class AppContainer:
    """
    Composition Root:
    - builds & caches models/services
    - no string lookups
    - guarantees one instance per dependency (per container)
    """

    def __init__(self, database=db) -> None:
        self._db = database

        # models cache
        self._building_model: Optional[BuildingModel] = None
        self._categories_model: Optional[ClassRoomCategoriesModel] = None
        self._class_rooms_model: Optional[ClassRoomsModel] = None
        self._motion_events_model: Optional[ClassroomMotionEventsModel] = None
        self._sensors_model: Optional[SensorsModel] = None
        self._users_model: Optional[UsersModel] = None

        # services cache
        self._rooms_service: Optional[RoomsService] = None
        self._building_service: Optional[BuildingService] = None
        self._home_service: Optional[HomeService] = None

    # --------------------
    # MODELS
    # --------------------
    @property
    def building_model(self) -> BuildingModel:
        if self._building_model is None:
            self._building_model = BuildingModel(self._db)
        return self._building_model

    @property
    def categories_model(self) -> ClassRoomCategoriesModel:
        if self._categories_model is None:
            self._categories_model = ClassRoomCategoriesModel(self._db)
        return self._categories_model

    @property
    def class_rooms_model(self) -> ClassRoomsModel:
        if self._class_rooms_model is None:
            self._class_rooms_model = ClassRoomsModel(self._db)
        return self._class_rooms_model

    @property
    def motion_events_model(self) -> ClassroomMotionEventsModel:
        if self._motion_events_model is None:
            self._motion_events_model = ClassroomMotionEventsModel(self._db)
        return self._motion_events_model

    @property
    def sensors_model(self) -> SensorsModel:
        if self._sensors_model is None:
            self._sensors_model = SensorsModel(self._db)
        return self._sensors_model

    @property
    def users_model(self) -> UsersModel:
        if self._users_model is None:
            self._users_model = UsersModel(self._db)
        return self._users_model

    # --------------------
    # SERVICES
    # --------------------
    @property
    def rooms_service(self) -> RoomsService:
        if self._rooms_service is None:
            self._rooms_service = RoomsService(
                self._db,
                self.class_rooms_model,
                self.motion_events_model,
                self.sensors_model,
            )
        return self._rooms_service

    @property
    def building_service(self) -> BuildingService:
        if self._building_service is None:
            self._building_service = BuildingService(
                self._db,
                self.building_model,
                self.class_rooms_model,
                self.rooms_service,
            )
        return self._building_service
    
    @property
    def home_service(self) -> HomeService:
        if self._home_service is None:
            self._home_service = HomeService(
                self._db,
                self.building_service,
                self.rooms_service,
                self.building_model,
                self.class_rooms_model,
                self.motion_events_model
            )
        return self._home_service


# container.py
from __future__ import annotations
from typing import Optional

# db
from core.create_database import db

# repositories
from repositories.building_repository import BuildingRepository, BuildingRepositoryMysql, BuildingRepositoryMock
from repositories.class_room_categories_repository import (
    ClassRoomCategoriesRepository,
    ClassRoomCategoriesRepositoryMysql,
    ClassRoomCategoriesRepositoryMock,
)
from repositories.classrooms_repository import ClassroomsRepository, ClassroomsRepositoryMysql, ClassroomsRepositoryMock
from repositories.classroom_motion_events_repository import (
    ClassroomMotionEventsRepository,
    ClassroomMotionEventsRepositoryMysql,
    ClassroomMotionEventsRepositoryMock,
)
from repositories.sensors_repository import SensorsRepository, SensorsRepositoryMysql, SensorsRepositoryMock
from repositories.users_repository import UsersRepository, UsersRepositoryMysql, UsersRepositoryMock


# services
from services.rooms_service import RoomsService
from services.building_service import BuildingService
from services.home_service import HomeService
from services.users_service import UsersService
from services.sensors_service import SensorsService
from services.categories_service import CategoriesService
from services.motion_events_service import MotionEventsService
from services.permission_service import PermissionService

class AppContainer:
    """
    Composition Root:
    - builds & caches models/services
    - no string lookups
    - guarantees one instance per dependency (per container)
    """

    def __init__(self, database=db) -> None:
        self._db = database

        # repositories cache
        self._building_model: Optional[BuildingRepository] = None
        self._categories_model: Optional[ClassRoomCategoriesRepository] = None
        self._class_rooms_model: Optional[ClassroomsRepository] = None
        self._motion_events_model: Optional[ClassroomMotionEventsRepository] = None
        self._sensors_model: Optional[SensorsRepository] = None
        self._users_model: Optional[UsersRepository] = None

        # services cache
        self._rooms_service = None
        self._building_service = None
        self._home_service = None
        self._users_service = None
        self._sensors_service = None
        self._categories_service = None
        self._motion_events_service = None
        self._permission_service = None

    # --------------------
    # REPOSITORIES
    # --------------------
    def _is_mock_db(self) -> bool:
        print(f"DB class: {self._db.__class__.__name__}")
        return self._db.__class__.__name__.lower() == "mockjsondb"

    @property
    def building_model(self) -> BuildingRepository:
        if self._building_model is None:
            repo_cls = BuildingRepositoryMock if self._is_mock_db() else BuildingRepositoryMysql
            self._building_model = repo_cls(self._db)
        return self._building_model

    @property
    def categories_model(self) -> ClassRoomCategoriesRepository:
        if self._categories_model is None:
            repo_cls = ClassRoomCategoriesRepositoryMock if self._is_mock_db() else ClassRoomCategoriesRepositoryMysql
            self._categories_model = repo_cls(self._db)
        return self._categories_model

    @property
    def class_rooms_model(self) -> ClassroomsRepository:
        if self._class_rooms_model is None:
            repo_cls = ClassroomsRepositoryMock if self._is_mock_db() else ClassroomsRepositoryMysql
            self._class_rooms_model = repo_cls(self._db)
        return self._class_rooms_model

    @property
    def motion_events_model(self) -> ClassroomMotionEventsRepository:
        if self._motion_events_model is None:
            repo_cls = ClassroomMotionEventsRepositoryMock if self._is_mock_db() else ClassroomMotionEventsRepositoryMysql
            self._motion_events_model = repo_cls(self._db)
        return self._motion_events_model

    @property
    def sensors_model(self) -> SensorsRepository:
        if self._sensors_model is None:
            repo_cls = SensorsRepositoryMock if self._is_mock_db() else SensorsRepositoryMysql
            self._sensors_model = repo_cls(self._db)
        return self._sensors_model

    @property
    def users_model(self) -> UsersRepository:
        if self._users_model is None:
            repo_cls = UsersRepositoryMock if self._is_mock_db() else UsersRepositoryMysql
            self._users_model = repo_cls(self._db)
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
    
    @property
    def users_service(self) -> UsersService:
        if self._users_service is None:
            self._users_service = UsersService(
                self._db,
                self.users_model,
            )
        return self._users_service
    
    @property
    def sensors_service(self) -> SensorsService:
        if self._sensors_service is None:
            self._sensors_service = SensorsService(
                self._db,
                self.sensors_model,
                self.class_rooms_model,
            )
        return self._sensors_service
    
    @property
    def categories_service(self) -> CategoriesService:
        if self._categories_service is None:
            self._categories_service = CategoriesService(
                self._db,
                self.categories_model,
            )
        return self._categories_service
    
    @property
    def motion_events_service(self) -> MotionEventsService:
        if self._motion_events_service is None:
            self._motion_events_service = MotionEventsService(
                self._db,
                self.motion_events_model,
                self.sensors_model,
            )
        return self._motion_events_service

    @property
    def permission_service(self) -> "PermissionService":
        if self._permission_service is None:
            # Prefer DB-backed provider; fall back to local in case of missing table/errors
            try:
                from core.infrastructure.permission_manager import (
                    PermissionDB,
                    PermissionLocal,
                )

                provider = PermissionDB(self._db)
                # quick probe to ensure provider works (may raise if table missing)
                try:
                    provider.get_permissions("home")
                except Exception:
                    provider = PermissionLocal()

                self._permission_service = PermissionService(provider)
            except Exception:
                # ultimate fallback
                from core.infrastructure.permission_manager import PermissionLocal

                self._permission_service = PermissionService(PermissionLocal())

        return self._permission_service


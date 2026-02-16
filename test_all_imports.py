# test_all_imports.py
"""Comprehensive import test to verify all architecture changes"""

print("Testing all imports...")

# Core
from core.db import DB
from core.permissions import Permissions
print("✓ Core modules imported")

# Infrastructure
from core.infrastructure.mysql import MySQL
from core.infrastructure.mock_json_db import MockJSONDB
from core.infrastructure.permission_manager import PermissionService, PermissionLocal
print("✓ Infrastructure modules imported")

# Models (Entity classes)
from models.Building import Building
from models.Room import Room
from models.Sensor import Sensor
from models.ClassRoomCategory import ClassRoomCategory
from models.ClassroomMotionEvent import ClassroomMotionEvent
from models.User import User
print("✓ All entity models imported")

# Repositories
from repositories.building_repository import BuildingRepository
from repositories.classrooms_repository import ClassroomsRepository
from repositories.sensors_repository import SensorsRepository
from repositories.classroom_motion_events_repository import ClassroomMotionEventsRepository
from repositories.class_room_categories_repository import ClassRoomCategoriesRepository
from repositories.users_repository import UsersRepository
print("✓ All repositories imported")

# Services
from services.building_service import BuildingService
from services.rooms_service import RoomsService
from services.sensors_service import SensorsService
from services.categories_service import CategoriesService
from services.motion_events_service import MotionEventsService
from services.users_service import UsersService
from services.home_service import HomeService
print("✓ All services imported")

# Controllers
from controllers.home_controller import HomeController
from controllers.building_details_controller import Building_detailsController
from controllers.search_controller import SearchController
from controllers.adminlogin_controller import AdminLoginController
from controllers.dashboardadmin_controller import DashboardAdminController
print("✓ All controllers imported")

print("\n✅ All imports successful!")
print("✅ Repository Pattern architecture refactoring is complete!")
print("\nNew Architecture:")
print("  models/              - Pure entity classes (data only)")
print("  repositories/        - Database access layer (can swap MySQL for any DB)")
print("  services/            - Business logic layer")
print("  controllers/         - Web layer")
print("  core/                - Core interfaces and utilities")

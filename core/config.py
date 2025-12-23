import os
from dotenv import load_dotenv

load_dotenv()

SENSORE_LOG_ACTIVITY = os.getenv("SENSORE_LOG_ACTIVITY")

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_SSL_REQUIRED = os.getenv("MYSQL_SSL_REQUIRED", "true").lower() == "true"

SECRET_JWT_KEY = os.getenv("SECRET_JWT_KEY")


SERVER_PORT = os.getenv("SERVER_PORT")
ENV_MODE = os.getenv("ENV_MODE")


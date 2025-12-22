import os
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_DATABASE_STAGING = os.getenv("MYSQL_DATABASE_STAGING")
ENV_MODE = os.getenv("ENV_MODE")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_SSL_REQUIRED = os.getenv("MYSQL_SSL_REQUIRED", "true").lower() == "true"

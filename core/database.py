from core.mysql import MySQL
from core.config import (
    MYSQL_HOST,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
    MYSQL_PORT,
    MYSQL_SSL_REQUIRED,
    MYSQL_DATABASE_STAGING,
    ENV_MODE
)

DB_NAME = MYSQL_DATABASE_STAGING
if ENV_MODE == "Production":
    DB_NAME = MYSQL_DATABASE

db = MySQL(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=DB_NAME,
    port=MYSQL_PORT,
    ssl_required=MYSQL_SSL_REQUIRED,
)

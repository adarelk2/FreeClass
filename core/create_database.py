from core.mysql import MySQL
from core.config import (
    MYSQL_HOST,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
    MYSQL_PORT,
    MYSQL_SSL_REQUIRED,

    ENV_MODE
)

db = MySQL(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE,
    port=MYSQL_PORT,
    ssl_required=MYSQL_SSL_REQUIRED,
)
from core.mysql import MySQL
from core.config import (
    MYSQL_HOST,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
    MYSQL_DATABASE_STAGING,
    MYSQL_HOST_STAGING,
    MYSQL_USER_STAGING,
    MYSQL_PASSWORD_STAGING,
    MYSQL_PORT,
    MYSQL_SSL_REQUIRED,

    ENV_MODE
)

if ENV_MODE == "Production":
    db = MySQL(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE,
    port=MYSQL_PORT,
    ssl_required=MYSQL_SSL_REQUIRED,
)
else:
    db = MySQL(
        host=MYSQL_HOST_STAGING,
        user=MYSQL_USER_STAGING,
        password=MYSQL_PASSWORD_STAGING,
        database=MYSQL_DATABASE_STAGING,
        port=MYSQL_PORT,
        ssl_required=MYSQL_SSL_REQUIRED,
    )

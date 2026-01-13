from core.infrastructure.mysql import MySQL
from core.infrastructure.mock_json_db import MockJSONDB
from core.config import (
    MYSQL_HOST,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
    MYSQL_PORT,
    MYSQL_SSL_REQUIRED,

    ENV_MODE
)

def createDatabase(_mode="production"):
    if _mode == "production":
        return MySQL(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            port=MYSQL_PORT,
            ssl_required=MYSQL_SSL_REQUIRED,
        )

    elif _mode == "develop":
        return MockJSONDB("database/mock_db.json")

    else:
        raise ValueError(f"Unknown ENV_MODE: {_mode}")

db = createDatabase(ENV_MODE.lower())
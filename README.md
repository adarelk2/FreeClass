# FreeClass – Real-Time Classroom Availability

FreeClass is a Flask-based backend project that converts occupancy inputs (sensor/simulator) into classroom availability data, with demo HTML templates for UI rendering.

## Environment modes

Runtime database backend is controlled by `ENV_MODE`:

| ENV_MODE | Backend |
|----------|---------|
| `develop` | JSON mock database (`database/mock_db.json`) |
| `production` | MySQL |

## Prerequisites

- Python 3.10+
- pip
- (Optional) MySQL server for `production` mode

## Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables (via `.env` or shell export):

- `ENV_MODE` (`develop` / `production`)
- `SERVER_PORT`
- `SECRET_JWT_KEY`
- `MYSQL_HOST`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`
- `MYSQL_PORT` (optional, default `3306`)
- `MYSQL_SSL_REQUIRED` (optional, default `true`)

> Note: In `develop` mode, FreeClass uses `database/mock_db.json` and does not require MySQL.

4. For MySQL mode, import the schema:

```bash
mysql -u <user> -p <database_name> < database/schema.sql
```

## Run the application

```bash
python3 main.py
```

The app exposes a controller-based route pattern:

- `/` (defaults to `home` controller)
- `/<controller>`

## Run tests

```bash
python3 -m unittest tests.test_unit
```

## Project structure (high-level)

- `main.py` – Flask entry point and request dispatch route.
- `core/` – app orchestration, configuration, controller loading, infrastructure.
- `controllers/` – request handlers per controller.
- `services/` – business logic.
- `repositories/` – DB/mock repository implementations and interfaces.
- `models/` – domain models.
- `database/` – SQL schema and mock JSON database.
- `templates/` – HTML templates (`templates/pages/` for page templates).
- `sensor.ino` – sensor-side sketch (ESP32/Arduino context).

## API collection

Postman collection is included at:

- `FreeClass_API_POSTMAN.json`

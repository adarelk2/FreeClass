# FreeClass – Real-Time Campus Space Availability (Backend-Focused)

FreeClass is a backend-first system that turns IoT occupancy signals (ESP32 or simulator) into **real-time classroom availability** for a campus.
The client side exists mainly to demonstrate UX/UI, and is located under `template/pages`.

---

## 🌍 Environment Modes & Database Selection

FreeClass supports multiple runtime modes controlled via the environment variable `ENV_MODE`.


| ENV_MODE value | Database backend |
| -------------- | ---------------- |
| develop        | MockJSONDB       |
| production     | MySQL            |

### Example

```bash
export ENV_MODE=develop
python main.py

export ENV_MODE=production
python main.py
```

---

## What this repo showcases

- **Real-time occupancy pipeline**: sensor event → API → MySQL → live availability views
- **Backend architecture & data modeling** for:
  - campus → buildings → rooms → sensors
  - motion/occupancy event logs + current status
- **Operational controls**: admin overrides (e.g., maintenance/closure) that take precedence over sensor data
- **Performance-minded querying**: aggregation, filtering, and dynamic query building for dashboards
- **Reliability considerations**: latency, sensor failure, stale updates, and safe fallbacks

---

## System at a glance

```
IoT Sensors (ESP32 / Simulator)
        ↓
Python Backend (REST API)
        ↓
MySQL (events + current status + history)
        ↓
UI templates (for demo) → template/pages
```

The backend provides consistent availability results even when schedules don’t match physical reality (“ghost occupancy”).

---

## Key capabilities

### Student-facing (API + demo UI)

- Campus-wide availability overview (total vacant rooms)
- Building and floor breakdown
- Room type filters (e.g., classrooms, labs, libraries)
- Recent activity tracking (last viewed rooms + live status)
- Weekly occupancy visualization (derived from historical data)

### Admin-facing (API + demo UI)

- Secure admin login
- Override room status (Available / Occupied / Maintenance)
- Manage rooms and sensor assignments
- Monitor utilization and data correctness

---

## Tech stack

**Backend**

- Python (REST API)
- IoT integration layer (simulated or physical)
- MySQL queries for aggregation + filtering

**Frontend (demo-only)**

- HTML5 + Tailwind CSS + Vanilla JS
- Pages/templates live in: `template/pages`

**Tooling**

- Git/GitHub, VS Code, Postman

---

## Project structure (high level)

> Exact filenames may vary, but the repository is organized around a backend core + templates:

- `core/` – application orchestration, routing/dispatch, configuration
- `models/` – database access and domain models (rooms, sensors, events, users)
- `services/` – business logic (availability calculations, filters, admin actions)
- `controllers/` – request handling (student/admin endpoints)
- `template/pages/` – demo UI pages (UX/UI only)

---

## Running locally (typical)

1. Create a MySQL database and import database/schema.sql
2. Configure environment variables (DB host/user/password, app port, ENV_MODE).
3. Install dependencies and run the server.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

## Why this matters

This project tackles real engineering challenges:

- bridging **physical signals** with **software truth**
- handling imperfect data and operational overrides
- delivering consistent results with **low latency**
- designing a backend that can scale from simulator to real hardware

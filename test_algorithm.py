#!/usr/bin/env python3
"""
Diagnostic script to debug room availability calculation.
Run this to see what's happening with the algorithm.
"""
import sys
from datetime import datetime, timedelta

# Test 1: Verify datetime arithmetic
print("=" * 60)
print("TEST 1: Datetime Arithmetic")
print("=" * 60)

now = datetime.utcnow()
print(f"Current time (UTC): {now}")
print(f"Activity window: 900 seconds (15 minutes)\n")

test_cases = [
    ("5 min ago", now - timedelta(seconds=300)),
    ("15 min ago", now - timedelta(seconds=900)),
    ("20 min ago", now - timedelta(seconds=1200)),
    ("1 hour ago", now - timedelta(seconds=3600)),
]

for label, event_time in test_cases:
    delta = (now - event_time).total_seconds()
    is_recent = 0 <= delta <= 900
    status = "BUSY" if is_recent else "AVAILABLE"
    print(f"{label:15} delta={delta:6.0f}s -> {status}")

# Test 2: String datetime parsing
print("\n" + "=" * 60)
print("TEST 2: String Datetime Parsing (MySQL format)")
print("=" * 60)

datetime_strings = [
    "2026-02-17 15:47:00",  # Recent
    "2026-02-17 15:30:00",  # 22 min ago
    "2026-02-17 14:50:00",  # ~1 hour ago
]

for dt_str in datetime_strings:
    try:
        parsed_time = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        delta = (now - parsed_time).total_seconds()
        is_recent = 0 <= delta <= 900
        status = "BUSY" if is_recent else "AVAILABLE"
        print(f"{dt_str} delta={delta:6.0f}s -> {status}")
    except Exception as e:
        print(f"{dt_str} ERROR: {e}")

# Test 3: ISO format parsing
print("\n" + "=" * 60)
print("TEST 3: ISO Format Datetime Parsing")
print("=" * 60)

iso_strings = [
    "2026-02-17T15:47:00+00:00",
    "2026-02-17T15:47:00Z",
]

for dt_str in iso_strings:
    try:
        parsed_time = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        delta = (now - parsed_time).total_seconds()
        is_recent = 0 <= delta <= 900
        status = "BUSY" if is_recent else "AVAILABLE"
        print(f"{dt_str} delta={delta:6.0f}s -> {status}")
    except Exception as e:
        print(f"{dt_str} ERROR: {e}")

# Test 4: Algorithm simulation
print("\n" + "=" * 60)
print("TEST 4: Algorithm Simulation")
print("=" * 60)

print("""
Algorithm:
1. Fetch all motion events (ordered by time DESC, limit 200)
2. For each event:
   - Parse event_time to datetime
   - Calculate delta = now - event_time
   - If 0 <= delta <= 900: mark room as BUSY
   - Otherwise: room is AVAILABLE
3. available_ids = all_rooms - busy_rooms
4. For display: status = "available" if room in available_ids else "busy"
""")

print("\nPossible Issues (if all rooms show as BUSY):")
print("  1. Event timestamps are in future (delta < 0)")
print("  2. Event timestamps are malformed and parsing fails")
print("  3. Activity_seconds config is very high or negative")
print("  4. All rooms actually DO have recent events")
print("  5. Timestamp timezone mismatch")

print("\nTo debug, check:")
print("  - SELECT COUNT(*) FROM classroom_motion_events")
print("  - SELECT event_time FROM classroom_motion_events ORDER BY event_time DESC LIMIT 5")
print("  - Check database clock: SELECT NOW()")

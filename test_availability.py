#!/usr/bin/env python3
"""
Test script to verify room availability algorithm.
"""
from datetime import datetime, timedelta

# Test the datetime parsing and filtering
def test_datetime_parsing():
    """Verify datetime parsing works"""
    now = datetime.utcnow()
    
    # Test with datetime object
    recent_event = now - timedelta(seconds=300)  # 5 min ago
    old_event = now - timedelta(seconds=1800)     # 30 min ago
    
    print("Testing datetime objects:")
    print(f"  Now: {now}")
    print(f"  Recent event (5 min ago): {recent_event}")
    print(f"  Old event (30 min ago): {old_event}")
    
    # Calculate deltas
    delta_recent = (now - recent_event).total_seconds()
    delta_old = (now - old_event).total_seconds()
    
    print(f"  Delta recent: {delta_recent} seconds")
    print(f"  Delta old: {delta_old} seconds")
    
    activity_seconds = 900  # 15 minutes
    
    print(f"\nActivity window: {activity_seconds} seconds (15 minutes)")
    print(f"  Recent event is {'BUSY' if 0 <= delta_recent <= activity_seconds else 'AVAILABLE'}")
    print(f"  Old event is {'BUSY' if 0 <= delta_old <= activity_seconds else 'AVAILABLE'}")
    
    # Test with string parsing
    print("\n\nTesting string datetime parsing:")
    recent_str = "2026-02-17 12:30:00"  # 5 minutes ago
    try:
        event_time = datetime.strptime(recent_str, '%Y-%m-%d %H:%M:%S')
        delta = (now - event_time).total_seconds()
        print(f"  String: {recent_str}")
        print(f"  Parsed: {event_time}")
        print(f"  Delta: {delta} seconds")
        print(f"  Status: {'BUSY' if 0 <= delta <= activity_seconds else 'AVAILABLE'}")
    except Exception as e:
        print(f"  Error parsing: {e}")

if __name__ == "__main__":
    test_datetime_parsing()

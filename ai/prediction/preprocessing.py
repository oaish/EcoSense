from datetime import datetime, timezone
from typing import List, Optional, Tuple


def normalize_datetime(dt: datetime) -> datetime:
    """Ensure datetime is timezone-aware in UTC for safe comparisons across SQLite and PostgreSQL."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def calculate_fill_rate_per_hour(
    readings: List[Tuple[datetime, float]],
) -> float:
    """Calculate the average fill accumulation rate (%/hour) across chronological readings.

    Handles irregular time intervals safely and avoids zero-division errors.
    If readings are decreasing or erratic, it calculates linear net progression or returns 0.0.

    Args:
        readings: Chronologically sorted list of (timestamp, fill_percentage) tuples.

    Returns:
        float: Accumulation rate in percentage points per hour (>= 0.0).
    """
    if len(readings) < 2:
        return 0.0

    total_time_hours = 0.0
    total_fill_diff = 0.0

    # Calculate interval-weighted fill changes in the current accumulation cycle
    for i in range(len(readings) - 1):
        t1, f1 = readings[i]
        t2, f2 = readings[i + 1]

        t1_norm = normalize_datetime(t1)
        t2_norm = normalize_datetime(t2)

        delta_hours = (t2_norm - t1_norm).total_seconds() / 3600.0
        if delta_hours <= 0:
            continue

        fill_delta = f2 - f1
        # If fill dropped significantly without a formal collection record, treat as partial drain/reset
        if fill_delta >= 0:
            total_fill_diff += fill_delta
            total_time_hours += delta_hours

    if total_time_hours <= 0:
        return 0.0

    rate = total_fill_diff / total_time_hours
    # Bound rate to realistic physical bounds (e.g. 0% to 100% per hour)
    return max(0.0, min(rate, 100.0))


def segment_cycle_readings(
    readings: List[Tuple[datetime, float]],
    last_collection_time: Optional[datetime] = None,
) -> List[Tuple[datetime, float]]:
    """Segment historical readings to include only observations from the current accumulation cycle

    (i.e., observations recorded strictly after the latest collection event).
    """
    if not readings:
        return []

    sorted_readings = sorted(readings, key=lambda x: normalize_datetime(x[0]))

    if last_collection_time is None:
        return sorted_readings

    last_coll_norm = normalize_datetime(last_collection_time)
    post_collection = [r for r in sorted_readings if normalize_datetime(r[0]) >= last_coll_norm]
    # If no readings occurred after collection, return at least the latest available reading
    return post_collection if post_collection else [sorted_readings[-1]]


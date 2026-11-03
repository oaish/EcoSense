import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ai.prediction.preprocessing import (
    calculate_fill_rate_per_hour,
    normalize_datetime,
    segment_cycle_readings,
)


@dataclass
class BinFillFeatures:
    """Standard feature vector for bin fill prediction."""

    bin_id: uuid.UUID
    current_fill_percentage: float
    recent_readings_count: int
    fill_rate_per_hour: float
    time_since_last_reading_hours: float
    time_since_last_collection_hours: Optional[float]
    last_collection_fill_after: Optional[float]
    disposal_events_count: int
    hour_of_day: int
    day_of_week: int
    horizon_hours: float
    waste_type_name: Optional[str] = None
    capacity_litres: Optional[float] = None


def extract_bin_features(
    bin_id: uuid.UUID,
    prediction_time: datetime,
    horizon_minutes: int,
    readings: List[Tuple[datetime, float]],
    collections: List[Tuple[datetime, Optional[float], Optional[float]]],
    disposals: List[Tuple[datetime, Optional[float]]],
    waste_type_name: Optional[str] = None,
    capacity_litres: Optional[float] = None,
    fallback_current_fill: float = 0.0,
) -> BinFillFeatures:
    """Extract chronological feature vector for a bin at a specific prediction timestamp.

    Strictly guarantees NO data leakage (ignores readings/events after prediction_time).

    Args:
        bin_id: UUID of target bin.
        prediction_time: The timestamp at which prediction is being requested.
        horizon_minutes: Prediction horizon ahead in minutes.
        readings: List of (recorded_at, fill_percentage) tuples.
        collections: List of (collected_at, fill_before, fill_after) tuples.
        disposals: List of (recorded_at, quantity_kg) tuples.
        waste_type_name: Name of bin's designated waste type.
        capacity_litres: Capacity of the bin.
        fallback_current_fill: Fallback fill level if no readings exist.

    Returns:
        BinFillFeatures: Extracted feature vector.
    """
    pred_time_norm = normalize_datetime(prediction_time)

    # 1. Filter out all future events to prevent data leakage
    past_readings = [r for r in readings if normalize_datetime(r[0]) <= pred_time_norm]
    past_readings.sort(key=lambda x: normalize_datetime(x[0]))

    past_collections = [c for c in collections if normalize_datetime(c[0]) <= pred_time_norm]
    past_collections.sort(key=lambda x: normalize_datetime(x[0]))

    past_disposals = [d for d in disposals if normalize_datetime(d[0]) <= pred_time_norm]

    # 2. Determine latest collection event
    latest_collection = past_collections[-1] if past_collections else None
    last_collection_time = latest_collection[0] if latest_collection else None
    last_collection_fill_after = (
        float(latest_collection[2])
        if latest_collection and latest_collection[2] is not None
        else None
    )

    time_since_last_coll_hours: Optional[float] = None
    if last_collection_time is not None:
        time_since_last_coll_hours = max(
            0.0,
            (pred_time_norm - normalize_datetime(last_collection_time)).total_seconds()
            / 3600.0,
        )

    # 3. Determine current fill & segment readings to current accumulation cycle
    current_cycle_readings = segment_cycle_readings(
        past_readings, last_collection_time=last_collection_time
    )

    if past_readings:
        latest_reading_time, latest_reading_fill = past_readings[-1]
        current_fill = float(latest_reading_fill)
        time_since_last_reading_hours = max(
            0.0,
            (pred_time_norm - normalize_datetime(latest_reading_time)).total_seconds()
            / 3600.0,
        )
    else:
        current_fill = float(fallback_current_fill)
        time_since_last_reading_hours = 0.0


    # 4. Calculate accumulation fill rate (%/hour) in the current accumulation cycle
    fill_rate = calculate_fill_rate_per_hour(current_cycle_readings)

    # 5. Temporal features
    horizon_hours = horizon_minutes / 60.0
    hour_of_day = prediction_time.hour
    day_of_week = prediction_time.weekday()

    return BinFillFeatures(
        bin_id=bin_id,
        current_fill_percentage=current_fill,
        recent_readings_count=len(past_readings),
        fill_rate_per_hour=fill_rate,
        time_since_last_reading_hours=round(time_since_last_reading_hours, 2),
        time_since_last_collection_hours=(
            round(time_since_last_coll_hours, 2)
            if time_since_last_coll_hours is not None
            else None
        ),
        last_collection_fill_after=last_collection_fill_after,
        disposal_events_count=len(past_disposals),
        hour_of_day=hour_of_day,
        day_of_week=day_of_week,
        horizon_hours=horizon_hours,
        waste_type_name=waste_type_name,
        capacity_litres=capacity_litres,
    )

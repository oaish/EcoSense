import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class SummaryMetrics(BaseModel):
    disposal_count: int
    total_collected_quantity_kg: Optional[float] = None
    total_processed_quantity_kg: Optional[float] = None
    total_recycled_quantity_kg: Optional[float] = None
    total_composted_quantity_kg: Optional[float] = None
    diversion_rate: Optional[float] = None


class OperationalMetrics(BaseModel):
    total_bins: int
    active_bins: int
    high_fill_bins: int
    damaged_bins: int
    missing_bins: int
    pending_reports: int
    in_progress_reports: int
    resolved_reports: int


class ParticipationMetrics(BaseModel):
    total_active_students: int
    participating_students: int
    participation_rate: Optional[float] = None


class GamificationMetrics(BaseModel):
    total_points_earned: int
    total_points_redeemed: int
    reward_redemptions_count: int


class PredictionMetrics(BaseModel):
    prediction_count: int
    high_fill_predictions: int


class AnalyticsSummary(BaseModel):
    period_start: datetime
    period_end: datetime
    summary: SummaryMetrics
    operations: OperationalMetrics
    participation: ParticipationMetrics
    gamification: GamificationMetrics
    predictions: PredictionMetrics


class WasteTypeMetric(BaseModel):
    waste_type_id: int
    waste_type_name: str
    disposal_count: int
    collected_quantity_kg: Optional[float] = None
    processed_quantity_kg: Optional[float] = None
    recycled_quantity_kg: Optional[float] = None
    composted_quantity_kg: Optional[float] = None


class LocationMetric(BaseModel):
    location_id: int
    location_name: str
    location_type: str
    building: str
    floor: str
    active_bin_count: int
    disposal_count: int
    collected_quantity_kg: Optional[float] = None
    processed_quantity_kg: Optional[float] = None
    recycled_quantity_kg: Optional[float] = None
    composted_quantity_kg: Optional[float] = None
    average_fill_percentage: Optional[float] = None


class TrendPoint(BaseModel):
    period: str
    disposal_count: int
    collected_quantity_kg: Optional[float] = None
    processed_quantity_kg: Optional[float] = None
    recycled_quantity_kg: Optional[float] = None
    composted_quantity_kg: Optional[float] = None


class TrendAnalytics(BaseModel):
    granularity: str
    data_points: List[TrendPoint]


class CollectionAnalytics(BaseModel):
    total_collections: int
    total_collected_quantity_kg: Optional[float] = None
    average_collected_quantity_kg: Optional[float] = None
    average_fill_before: Optional[float] = None
    average_fill_after: Optional[float] = None
    collections_by_day: List[Dict[str, Any]]
    frequently_collected_bins: List[Dict[str, Any]]


class BinDetailSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bin_id: uuid.UUID
    bin_code: str
    location_name: str
    waste_type: str
    current_fill_percentage: Optional[float] = None
    status: str


class BinFillAnalytics(BaseModel):
    average_fill_percentage: Optional[float] = None
    max_fill_percentage: Optional[float] = None
    min_fill_percentage: Optional[float] = None
    total_readings: int
    high_fill_reading_count: int
    high_fill_threshold: float
    high_fill_bins: List[BinDetailSummary]


class AlertItem(BaseModel):
    alert_type: str
    severity: str
    title: str
    description: str
    bin_id: Optional[uuid.UUID] = None
    bin_code: Optional[str] = None
    location_name: Optional[str] = None
    waste_type_name: Optional[str] = None
    related_id: Optional[str] = None
    observed_at: datetime


class ReportAnalytics(BaseModel):
    total_reports: int
    pending_reports: int
    in_progress_reports: int
    resolved_reports: int
    rejected_reports: int
    reports_by_type: Dict[str, int]
    reports_by_location: List[Dict[str, Any]]
    average_resolution_time_hours: Optional[float] = None


class ProcessingAnalytics(BaseModel):
    total_processing_records: int
    total_processed_quantity_kg: Optional[float] = None
    total_recycled_quantity_kg: Optional[float] = None
    total_composted_quantity_kg: Optional[float] = None
    diversion_rate: Optional[float] = None
    processing_by_waste_type: List[Dict[str, Any]]
    processing_by_location: List[Dict[str, Any]]


class ParticipationAnalytics(BaseModel):
    total_active_students: int
    students_with_at_least_one_disposal: int
    unique_participating_students: int
    disposal_records_count: int
    reports_submitted_count: int
    reports_resolved_count: int
    participation_rate: Optional[float] = None


class GamificationAnalytics(BaseModel):
    total_points_earned: int
    total_points_redeemed: int
    earning_transactions_count: int
    reward_redemptions_count: int
    unique_participating_students: int
    points_earned_by_action: Dict[str, int]
    most_redeemed_rewards: List[Dict[str, Any]]


class PredictionAnalytics(BaseModel):
    total_predictions: int
    average_predicted_fill: Optional[float] = None
    max_predicted_fill: Optional[float] = None
    high_fill_predictions_count: int
    predictions_by_model_version: Dict[str, int]
    predictions_by_bin: List[Dict[str, Any]]


class ClassificationAnalytics(BaseModel):
    total_classifications: int
    average_confidence: Optional[float] = None
    low_confidence_count: int
    classifications_by_waste_type: Dict[str, int]
    classifications_by_model_version: Dict[str, int]

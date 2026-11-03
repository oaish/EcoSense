import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.bin import Bin
from app.models.classification import WasteClassification
from app.models.collection import CollectionRecord
from app.models.disposal import DisposalRecord
from app.models.fill_reading import BinFillReading
from app.models.gamification import PointTransaction, Reward, RewardRedemption
from app.models.location import Location
from app.models.prediction import FillPrediction
from app.models.processing import ProcessingRecord
from app.models.report import WasteReport
from app.models.role import Role
from app.models.user import User
from app.models.waste_type import WasteType
from app.schemas.analytics import (
    AlertItem,
    AnalyticsSummary,
    BinDetailSummary,
    BinFillAnalytics,
    ClassificationAnalytics,
    CollectionAnalytics,
    GamificationAnalytics,
    GamificationMetrics,
    LocationMetric,
    OperationalMetrics,
    ParticipationAnalytics,
    ParticipationMetrics,
    PredictionAnalytics,
    PredictionMetrics,
    ProcessingAnalytics,
    ReportAnalytics,
    SummaryMetrics,
    TrendAnalytics,
    TrendPoint,
    WasteTypeMetric,
)


def _normalize_date_range(
    start_date: Optional[datetime], end_date: Optional[datetime]
) -> Tuple[datetime, datetime]:
    """
    Normalizes time range parameters.
    Default: previous DEFAULT_ANALYTICS_DAYS (30 days) from now.
    Semantics: start_date is inclusive (>=), end_date is exclusive (<).
    Ensures timezone awareness (UTC).
    """
    now = datetime.now(timezone.utc)
    if end_date is None:
        end_date = now
    elif end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)

    if start_date is None:
        start_date = end_date - timedelta(days=settings.DEFAULT_ANALYTICS_DAYS)
    elif start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)

    return start_date, end_date


def get_analytics_summary(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> AnalyticsSummary:
    """
    Generates a high-level summary of campus waste management metrics for the specified period.
    All aggregation is done database-side without modifying operational records.
    """
    start_dt, end_dt = _normalize_date_range(start_date, end_date)

    # 1. Summary Metrics
    disposal_count = (
        db.query(sa.func.count(DisposalRecord.disposal_id))
        .filter(
            DisposalRecord.recorded_at >= start_dt,
            DisposalRecord.recorded_at < end_dt,
        )
        .scalar()
        or 0
    )

    collected_sum = (
        db.query(sa.func.sum(CollectionRecord.collected_quantity_kg))
        .filter(
            CollectionRecord.collected_at >= start_dt,
            CollectionRecord.collected_at < end_dt,
        )
        .scalar()
    )
    total_collected_kg = float(collected_sum) if collected_sum is not None else None

    # Processing aggregates
    proc_aggregates = (
        db.query(
            sa.func.sum(ProcessingRecord.quantity_kg).label("total_processed"),
            sa.func.sum(
                sa.case(
                    (ProcessingRecord.processing_type == "RECYCLING", ProcessingRecord.quantity_kg),
                    else_=0,
                )
            ).label("total_recycled"),
            sa.func.sum(
                sa.case(
                    (ProcessingRecord.processing_type == "COMPOSTING", ProcessingRecord.quantity_kg),
                    else_=0,
                )
            ).label("total_composted"),
        )
        .filter(
            ProcessingRecord.processed_at >= start_dt,
            ProcessingRecord.processed_at < end_dt,
        )
        .first()
    )

    total_processed_kg = (
        float(proc_aggregates.total_processed)
        if proc_aggregates and proc_aggregates.total_processed is not None
        else None
    )
    total_recycled_kg = (
        float(proc_aggregates.total_recycled)
        if proc_aggregates and proc_aggregates.total_recycled is not None and total_processed_kg is not None
        else None
    )
    total_composted_kg = (
        float(proc_aggregates.total_composted)
        if proc_aggregates and proc_aggregates.total_composted is not None and total_processed_kg is not None
        else None
    )

    # Diversion rate calculation
    diversion_rate: Optional[float] = None
    if total_collected_kg is not None and total_collected_kg > 0:
        if total_processed_kg is not None:
            diversion_rate = round((total_processed_kg / total_collected_kg) * 100.0, 2)
        else:
            diversion_rate = 0.0

    summary_metrics = SummaryMetrics(
        disposal_count=disposal_count,
        total_collected_quantity_kg=total_collected_kg,
        total_processed_quantity_kg=total_processed_kg,
        total_recycled_quantity_kg=total_recycled_kg,
        total_composted_quantity_kg=total_composted_kg,
        diversion_rate=diversion_rate,
    )

    # 2. Operational Metrics
    total_bins = db.query(sa.func.count(Bin.bin_id)).scalar() or 0
    active_bins = (
        db.query(sa.func.count(Bin.bin_id)).filter(Bin.status == "ACTIVE").scalar() or 0
    )
    high_fill_bins = (
        db.query(sa.func.count(Bin.bin_id))
        .filter(
            Bin.status == "ACTIVE",
            Bin.current_fill_percentage >= settings.HIGH_FILL_THRESHOLD,
        )
        .scalar()
        or 0
    )
    damaged_bins = (
        db.query(sa.func.count(Bin.bin_id)).filter(Bin.status == "DAMAGED").scalar() or 0
    )
    missing_bins = (
        db.query(sa.func.count(Bin.bin_id)).filter(Bin.status == "MISSING").scalar() or 0
    )

    report_status_counts = dict(
        db.query(WasteReport.status, sa.func.count(WasteReport.report_id))
        .filter(
            WasteReport.created_at >= start_dt,
            WasteReport.created_at < end_dt,
        )
        .group_by(WasteReport.status)
        .all()
    )
    pending_reports = report_status_counts.get("PENDING", 0)
    in_progress_reports = report_status_counts.get("IN_PROGRESS", 0)
    resolved_reports = report_status_counts.get("RESOLVED", 0)

    operational_metrics = OperationalMetrics(
        total_bins=total_bins,
        active_bins=active_bins,
        high_fill_bins=high_fill_bins,
        damaged_bins=damaged_bins,
        missing_bins=missing_bins,
        pending_reports=pending_reports,
        in_progress_reports=in_progress_reports,
        resolved_reports=resolved_reports,
    )

    # 3. Participation Metrics
    student_role = db.query(Role).filter(Role.role_name == "STUDENT").first()
    student_role_id = student_role.role_id if student_role else None

    total_active_students = (
        db.query(sa.func.count(User.user_id))
        .filter(User.role_id == student_role_id, User.is_active == True)  # noqa: E712
        .scalar()
        or 0
        if student_role_id
        else 0
    )

    participating_students = (
        db.query(sa.func.count(sa.distinct(DisposalRecord.user_id)))
        .join(User, DisposalRecord.user_id == User.user_id)
        .filter(
            User.role_id == student_role_id,
            DisposalRecord.recorded_at >= start_dt,
            DisposalRecord.recorded_at < end_dt,
        )
        .scalar()
        or 0
        if student_role_id
        else 0
    )

    participation_rate: Optional[float] = None
    if total_active_students > 0:
        participation_rate = round(
            (participating_students / total_active_students) * 100.0, 2
        )

    participation_metrics = ParticipationMetrics(
        total_active_students=total_active_students,
        participating_students=participating_students,
        participation_rate=participation_rate,
    )

    # 4. Gamification Metrics
    points_earned = (
        db.query(sa.func.sum(PointTransaction.points))
        .filter(
            PointTransaction.points > 0,
            PointTransaction.created_at >= start_dt,
            PointTransaction.created_at < end_dt,
        )
        .scalar()
        or 0
    )

    points_redeemed = (
        db.query(sa.func.sum(sa.func.abs(PointTransaction.points)))
        .filter(
            PointTransaction.points < 0,
            PointTransaction.created_at >= start_dt,
            PointTransaction.created_at < end_dt,
        )
        .scalar()
        or 0
    )

    redemptions_count = (
        db.query(sa.func.count(RewardRedemption.redemption_id))
        .filter(
            RewardRedemption.created_at >= start_dt,
            RewardRedemption.created_at < end_dt,
        )
        .scalar()
        or 0
    )

    gamification_metrics = GamificationMetrics(
        total_points_earned=int(points_earned),
        total_points_redeemed=int(points_redeemed),
        reward_redemptions_count=redemptions_count,
    )

    # 5. Prediction Metrics
    prediction_count = (
        db.query(sa.func.count(FillPrediction.prediction_id))
        .filter(
            FillPrediction.created_at >= start_dt,
            FillPrediction.created_at < end_dt,
        )
        .scalar()
        or 0
    )

    high_fill_predictions = (
        db.query(sa.func.count(FillPrediction.prediction_id))
        .filter(
            FillPrediction.created_at >= start_dt,
            FillPrediction.created_at < end_dt,
            FillPrediction.predicted_fill_percentage >= settings.HIGH_FILL_THRESHOLD,
        )
        .scalar()
        or 0
    )

    prediction_metrics = PredictionMetrics(
        prediction_count=prediction_count,
        high_fill_predictions=high_fill_predictions,
    )

    return AnalyticsSummary(
        period_start=start_dt,
        period_end=end_dt,
        summary=summary_metrics,
        operations=operational_metrics,
        participation=participation_metrics,
        gamification=gamification_metrics,
        predictions=prediction_metrics,
    )


def get_waste_type_analytics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    location_id: Optional[int] = None,
) -> List[WasteTypeMetric]:
    """
    Returns waste activity grouped by waste type, derived relationally without redundant tables.
    """
    start_dt, end_dt = _normalize_date_range(start_date, end_date)

    waste_types = db.query(WasteType).order_by(WasteType.name).all()

    # 1. Disposal counts by waste type
    disp_query = (
        db.query(Bin.waste_type_id, sa.func.count(DisposalRecord.disposal_id).label("cnt"))
        .join(DisposalRecord, DisposalRecord.bin_id == Bin.bin_id)
        .filter(
            DisposalRecord.recorded_at >= start_dt,
            DisposalRecord.recorded_at < end_dt,
        )
    )
    if location_id is not None:
        disp_query = disp_query.filter(Bin.location_id == location_id)
    disp_map = dict(disp_query.group_by(Bin.waste_type_id).all())

    # 2. Collection quantities by waste type
    col_query = (
        db.query(
            Bin.waste_type_id,
            sa.func.sum(CollectionRecord.collected_quantity_kg).label("total_kg"),
        )
        .join(CollectionRecord, CollectionRecord.bin_id == Bin.bin_id)
        .filter(
            CollectionRecord.collected_at >= start_dt,
            CollectionRecord.collected_at < end_dt,
        )
    )
    if location_id is not None:
        col_query = col_query.filter(Bin.location_id == location_id)
    col_map = dict(col_query.group_by(Bin.waste_type_id).all())

    # 3. Processing quantities by waste type
    proc_query = (
        db.query(
            Bin.waste_type_id,
            sa.func.sum(ProcessingRecord.quantity_kg).label("proc_kg"),
            sa.func.sum(
                sa.case(
                    (ProcessingRecord.processing_type == "RECYCLING", ProcessingRecord.quantity_kg),
                    else_=0,
                )
            ).label("rec_kg"),
            sa.func.sum(
                sa.case(
                    (ProcessingRecord.processing_type == "COMPOSTING", ProcessingRecord.quantity_kg),
                    else_=0,
                )
            ).label("comp_kg"),
        )
        .join(CollectionRecord, ProcessingRecord.collection_id == CollectionRecord.collection_id)
        .join(Bin, CollectionRecord.bin_id == Bin.bin_id)
        .filter(
            ProcessingRecord.processed_at >= start_dt,
            ProcessingRecord.processed_at < end_dt,
        )
    )
    if location_id is not None:
        proc_query = proc_query.filter(Bin.location_id == location_id)
    proc_results = {row.waste_type_id: row for row in proc_query.group_by(Bin.waste_type_id).all()}

    metrics = []
    for wt in waste_types:
        disp_count = disp_map.get(wt.waste_type_id, 0)
        col_kg = col_map.get(wt.waste_type_id)
        proc_data = proc_results.get(wt.waste_type_id)

        metrics.append(
            WasteTypeMetric(
                waste_type_id=wt.waste_type_id,
                waste_type_name=wt.name,
                disposal_count=disp_count,
                collected_quantity_kg=float(col_kg) if col_kg is not None else None,
                processed_quantity_kg=float(proc_data.proc_kg) if proc_data and proc_data.proc_kg is not None else None,
                recycled_quantity_kg=float(proc_data.rec_kg) if proc_data and proc_data.rec_kg is not None and proc_data.proc_kg is not None else None,
                composted_quantity_kg=float(proc_data.comp_kg) if proc_data and proc_data.comp_kg is not None and proc_data.proc_kg is not None else None,
            )
        )

    return metrics


def get_location_analytics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[LocationMetric]:
    """
    Returns metrics grouped by physical campus location.
    """
    start_dt, end_dt = _normalize_date_range(start_date, end_date)

    locations = db.query(Location).order_by(Location.name).all()

    # Active bin count per location
    bin_counts = dict(
        db.query(Bin.location_id, sa.func.count(Bin.bin_id))
        .filter(Bin.status == "ACTIVE")
        .group_by(Bin.location_id)
        .all()
    )

    # Disposals per location
    disp_counts = dict(
        db.query(Bin.location_id, sa.func.count(DisposalRecord.disposal_id))
        .join(DisposalRecord, DisposalRecord.bin_id == Bin.bin_id)
        .filter(
            DisposalRecord.recorded_at >= start_dt,
            DisposalRecord.recorded_at < end_dt,
        )
        .group_by(Bin.location_id)
        .all()
    )

    # Collection quantities per location
    col_sums = dict(
        db.query(
            Bin.location_id,
            sa.func.sum(CollectionRecord.collected_quantity_kg),
        )
        .join(CollectionRecord, CollectionRecord.bin_id == Bin.bin_id)
        .filter(
            CollectionRecord.collected_at >= start_dt,
            CollectionRecord.collected_at < end_dt,
        )
        .group_by(Bin.location_id)
        .all()
    )

    # Processing quantities per location
    proc_query = (
        db.query(
            Bin.location_id,
            sa.func.sum(ProcessingRecord.quantity_kg).label("proc_kg"),
            sa.func.sum(
                sa.case(
                    (ProcessingRecord.processing_type == "RECYCLING", ProcessingRecord.quantity_kg),
                    else_=0,
                )
            ).label("rec_kg"),
            sa.func.sum(
                sa.case(
                    (ProcessingRecord.processing_type == "COMPOSTING", ProcessingRecord.quantity_kg),
                    else_=0,
                )
            ).label("comp_kg"),
        )
        .join(CollectionRecord, ProcessingRecord.collection_id == CollectionRecord.collection_id)
        .join(Bin, CollectionRecord.bin_id == Bin.bin_id)
        .filter(
            ProcessingRecord.processed_at >= start_dt,
            ProcessingRecord.processed_at < end_dt,
        )
        .group_by(Bin.location_id)
        .all()
    )
    proc_map = {row.location_id: row for row in proc_query}

    # Average fill percentage per location
    reading_avg_query = (
        db.query(
            Bin.location_id,
            sa.func.avg(BinFillReading.fill_percentage).label("avg_fill"),
        )
        .join(BinFillReading, BinFillReading.bin_id == Bin.bin_id)
        .filter(
            BinFillReading.recorded_at >= start_dt,
            BinFillReading.recorded_at < end_dt,
        )
        .group_by(Bin.location_id)
        .all()
    )
    reading_avg_map = {row.location_id: row.avg_fill for row in reading_avg_query}

    current_bin_avg_query = (
        db.query(
            Bin.location_id,
            sa.func.avg(Bin.current_fill_percentage).label("avg_fill"),
        )
        .filter(Bin.status == "ACTIVE", Bin.current_fill_percentage.isnot(None))
        .group_by(Bin.location_id)
        .all()
    )
    current_bin_avg_map = {row.location_id: row.avg_fill for row in current_bin_avg_query}

    metrics = []
    for loc in locations:
        disp_cnt = disp_counts.get(loc.location_id, 0)
        col_kg = col_sums.get(loc.location_id)
        proc_data = proc_map.get(loc.location_id)
        active_bins = bin_counts.get(loc.location_id, 0)

        avg_fill = reading_avg_map.get(loc.location_id)
        if avg_fill is None:
            avg_fill = current_bin_avg_map.get(loc.location_id)

        metrics.append(
            LocationMetric(
                location_id=loc.location_id,
                location_name=loc.name,
                location_type=loc.location_type,
                building=loc.building or "",
                floor=loc.floor or "",
                active_bin_count=active_bins,
                disposal_count=disp_cnt,
                collected_quantity_kg=float(col_kg) if col_kg is not None else None,
                processed_quantity_kg=float(proc_data.proc_kg) if proc_data and proc_data.proc_kg is not None else None,
                recycled_quantity_kg=float(proc_data.rec_kg) if proc_data and proc_data.rec_kg is not None and proc_data.proc_kg is not None else None,
                composted_quantity_kg=float(proc_data.comp_kg) if proc_data and proc_data.comp_kg is not None and proc_data.proc_kg is not None else None,
                average_fill_percentage=round(float(avg_fill), 2) if avg_fill is not None else None,
            )
        )

    return metrics


def get_trend_analytics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    granularity: str = "day",
) -> TrendAnalytics:
    """
    Returns time-series records for waste trends (disposals, collections, processing).
    Supports granularities: 'day', 'week', 'month'.
    """
    start_dt, end_dt = _normalize_date_range(start_date, end_date)

    disp_query = (
        db.query(
            sa.func.date(DisposalRecord.recorded_at).label("d_date"),
            sa.func.count(DisposalRecord.disposal_id).label("cnt"),
        )
        .filter(
            DisposalRecord.recorded_at >= start_dt,
            DisposalRecord.recorded_at < end_dt,
        )
        .group_by(sa.func.date(DisposalRecord.recorded_at))
        .all()
    )

    col_query = (
        db.query(
            sa.func.date(CollectionRecord.collected_at).label("c_date"),
            sa.func.sum(CollectionRecord.collected_quantity_kg).label("total_kg"),
        )
        .filter(
            CollectionRecord.collected_at >= start_dt,
            CollectionRecord.collected_at < end_dt,
        )
        .group_by(sa.func.date(CollectionRecord.collected_at))
        .all()
    )

    proc_query = (
        db.query(
            sa.func.date(ProcessingRecord.processed_at).label("p_date"),
            sa.func.sum(ProcessingRecord.quantity_kg).label("proc_kg"),
            sa.func.sum(
                sa.case(
                    (ProcessingRecord.processing_type == "RECYCLING", ProcessingRecord.quantity_kg),
                    else_=0,
                )
            ).label("rec_kg"),
            sa.func.sum(
                sa.case(
                    (ProcessingRecord.processing_type == "COMPOSTING", ProcessingRecord.quantity_kg),
                    else_=0,
                )
            ).label("comp_kg"),
        )
        .filter(
            ProcessingRecord.processed_at >= start_dt,
            ProcessingRecord.processed_at < end_dt,
        )
        .group_by(sa.func.date(ProcessingRecord.processed_at))
        .all()
    )

    def format_period_key(d: Any, gran: str) -> str:
        if isinstance(d, str):
            dt = datetime.strptime(d[:10], "%Y-%m-%d")
        else:
            dt = datetime(d.year, d.month, d.day)

        if gran == "month":
            return dt.strftime("%Y-%m")
        elif gran == "week":
            return f"{dt.year}-W{dt.isocalendar()[1]:02d}"
        else:
            return dt.strftime("%Y-%m-%d")

    points_by_period: Dict[str, Dict[str, Any]] = {}

    for row in disp_query:
        if row.d_date is None:
            continue
        p = format_period_key(row.d_date, granularity)
        if p not in points_by_period:
            points_by_period[p] = {
                "disposal_count": 0,
                "collected_quantity_kg": None,
                "processed_quantity_kg": None,
                "recycled_quantity_kg": None,
                "composted_quantity_kg": None,
            }
        points_by_period[p]["disposal_count"] += row.cnt

    for row in col_query:
        if row.c_date is None:
            continue
        p = format_period_key(row.c_date, granularity)
        if p not in points_by_period:
            points_by_period[p] = {
                "disposal_count": 0,
                "collected_quantity_kg": None,
                "processed_quantity_kg": None,
                "recycled_quantity_kg": None,
                "composted_quantity_kg": None,
            }
        val = float(row.total_kg) if row.total_kg is not None else None
        if val is not None:
            curr = points_by_period[p]["collected_quantity_kg"]
            points_by_period[p]["collected_quantity_kg"] = round((curr or 0.0) + val, 2)

    for row in proc_query:
        if row.p_date is None:
            continue
        p = format_period_key(row.p_date, granularity)
        if p not in points_by_period:
            points_by_period[p] = {
                "disposal_count": 0,
                "collected_quantity_kg": None,
                "processed_quantity_kg": None,
                "recycled_quantity_kg": None,
                "composted_quantity_kg": None,
            }
        if row.proc_kg is not None:
            curr = points_by_period[p]["processed_quantity_kg"]
            points_by_period[p]["processed_quantity_kg"] = round((curr or 0.0) + float(row.proc_kg), 2)
        if row.rec_kg is not None:
            curr = points_by_period[p]["recycled_quantity_kg"]
            points_by_period[p]["recycled_quantity_kg"] = round((curr or 0.0) + float(row.rec_kg), 2)
        if row.comp_kg is not None:
            curr = points_by_period[p]["composted_quantity_kg"]
            points_by_period[p]["composted_quantity_kg"] = round((curr or 0.0) + float(row.comp_kg), 2)

    sorted_periods = sorted(points_by_period.keys())
    data_points = [
        TrendPoint(
            period=p,
            disposal_count=points_by_period[p]["disposal_count"],
            collected_quantity_kg=points_by_period[p]["collected_quantity_kg"],
            processed_quantity_kg=points_by_period[p]["processed_quantity_kg"],
            recycled_quantity_kg=points_by_period[p]["recycled_quantity_kg"],
            composted_quantity_kg=points_by_period[p]["composted_quantity_kg"],
        )
        for p in sorted_periods
    ]

    return TrendAnalytics(granularity=granularity, data_points=data_points)


def get_collection_analytics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    location_id: Optional[int] = None,
    bin_id: Optional[uuid.UUID] = None,
) -> CollectionAnalytics:
    """
    Returns aggregated metrics on waste collections, fill transitions, and frequently serviced bins.
    """
    start_dt, end_dt = _normalize_date_range(start_date, end_date)

    agg = (
        db.query(
            sa.func.count(CollectionRecord.collection_id).label("total_cols"),
            sa.func.sum(CollectionRecord.collected_quantity_kg).label("total_kg"),
            sa.func.avg(CollectionRecord.collected_quantity_kg).label("avg_kg"),
            sa.func.avg(CollectionRecord.fill_level_before).label("avg_before"),
            sa.func.avg(CollectionRecord.fill_level_after).label("avg_after"),
        )
        .join(Bin, CollectionRecord.bin_id == Bin.bin_id)
        .filter(
            CollectionRecord.collected_at >= start_dt,
            CollectionRecord.collected_at < end_dt,
        )
    )
    if location_id is not None:
        agg = agg.filter(Bin.location_id == location_id)
    if bin_id is not None:
        agg = agg.filter(CollectionRecord.bin_id == bin_id)

    row = agg.first()
    total_cols = row.total_cols if row else 0
    total_kg = float(row.total_kg) if row and row.total_kg is not None else None
    avg_kg = round(float(row.avg_kg), 2) if row and row.avg_kg is not None else None
    avg_before = round(float(row.avg_before), 2) if row and row.avg_before is not None else None
    avg_after = round(float(row.avg_after), 2) if row and row.avg_after is not None else None

    # Collections by day
    day_query = (
        db.query(
            sa.func.date(CollectionRecord.collected_at).label("c_date"),
            sa.func.count(CollectionRecord.collection_id).label("cnt"),
            sa.func.sum(CollectionRecord.collected_quantity_kg).label("total_kg"),
        )
        .join(Bin, CollectionRecord.bin_id == Bin.bin_id)
        .filter(
            CollectionRecord.collected_at >= start_dt,
            CollectionRecord.collected_at < end_dt,
        )
    )
    if location_id is not None:
        day_query = day_query.filter(Bin.location_id == location_id)
    if bin_id is not None:
        day_query = day_query.filter(CollectionRecord.bin_id == bin_id)

    day_rows = (
        day_query.group_by(sa.func.date(CollectionRecord.collected_at))
        .order_by(sa.func.date(CollectionRecord.collected_at))
        .all()
    )
    collections_by_day = [
        {
            "date": str(r.c_date),
            "collection_count": r.cnt,
            "total_quantity_kg": float(r.total_kg) if r.total_kg is not None else None,
        }
        for r in day_rows
    ]

    # Frequently collected bins
    freq_query = (
        db.query(
            Bin.bin_id,
            Bin.bin_code,
            Location.name.label("location_name"),
            WasteType.name.label("waste_type"),
            sa.func.count(CollectionRecord.collection_id).label("col_count"),
            sa.func.avg(CollectionRecord.fill_level_before).label("avg_fill_before"),
        )
        .join(CollectionRecord, CollectionRecord.bin_id == Bin.bin_id)
        .join(Location, Bin.location_id == Location.location_id)
        .join(WasteType, Bin.waste_type_id == WasteType.waste_type_id)
        .filter(
            CollectionRecord.collected_at >= start_dt,
            CollectionRecord.collected_at < end_dt,
        )
    )
    if location_id is not None:
        freq_query = freq_query.filter(Bin.location_id == location_id)
    if bin_id is not None:
        freq_query = freq_query.filter(CollectionRecord.bin_id == bin_id)

    freq_rows = (
        freq_query.group_by(Bin.bin_id, Bin.bin_code, Location.name, WasteType.name)
        .order_by(sa.func.count(CollectionRecord.collection_id).desc())
        .limit(10)
        .all()
    )
    frequently_collected = [
        {
            "bin_id": str(r.bin_id),
            "bin_code": r.bin_code,
            "location_name": r.location_name,
            "waste_type": r.waste_type,
            "collection_count": r.col_count,
            "average_fill_before": round(float(r.avg_fill_before), 2) if r.avg_fill_before is not None else None,
        }
        for r in freq_rows
    ]

    return CollectionAnalytics(
        total_collections=total_cols,
        total_collected_quantity_kg=total_kg,
        average_collected_quantity_kg=avg_kg,
        average_fill_before=avg_before,
        average_fill_after=avg_after,
        collections_by_day=collections_by_day,
        frequently_collected_bins=frequently_collected,
    )


def get_bin_fill_analytics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    location_id: Optional[int] = None,
    waste_type_id: Optional[int] = None,
    bin_id: Optional[uuid.UUID] = None,
    threshold: Optional[float] = None,
) -> BinFillAnalytics:
    """
    Returns analytics on bin fill readings and identifies high-fill operational conditions.
    """
    start_dt, end_dt = _normalize_date_range(start_date, end_date)
    high_threshold = threshold if threshold is not None else settings.HIGH_FILL_THRESHOLD

    # Reading statistics in range
    read_query = (
        db.query(
            sa.func.avg(BinFillReading.fill_percentage).label("avg_fill"),
            sa.func.max(BinFillReading.fill_percentage).label("max_fill"),
            sa.func.min(BinFillReading.fill_percentage).label("min_fill"),
            sa.func.count(BinFillReading.reading_id).label("total_readings"),
            sa.func.sum(
                sa.case(
                    (BinFillReading.fill_percentage >= high_threshold, 1),
                    else_=0,
                )
            ).label("high_readings"),
        )
        .join(Bin, BinFillReading.bin_id == Bin.bin_id)
        .filter(
            BinFillReading.recorded_at >= start_dt,
            BinFillReading.recorded_at < end_dt,
        )
    )
    if location_id is not None:
        read_query = read_query.filter(Bin.location_id == location_id)
    if waste_type_id is not None:
        read_query = read_query.filter(Bin.waste_type_id == waste_type_id)
    if bin_id is not None:
        read_query = read_query.filter(BinFillReading.bin_id == bin_id)

    row = read_query.first()
    avg_fill = round(float(row.avg_fill), 2) if row and row.avg_fill is not None else None
    max_fill = float(row.max_fill) if row and row.max_fill is not None else None
    min_fill = float(row.min_fill) if row and row.min_fill is not None else None
    total_readings = row.total_readings if row else 0
    high_readings = int(row.high_readings) if row and row.high_readings is not None else 0

    # Currently high fill bins
    bin_q = (
        db.query(
            Bin.bin_id,
            Bin.bin_code,
            Location.name.label("location_name"),
            WasteType.name.label("waste_type"),
            Bin.current_fill_percentage,
            Bin.status,
        )
        .join(Location, Bin.location_id == Location.location_id)
        .join(WasteType, Bin.waste_type_id == WasteType.waste_type_id)
        .filter(
            Bin.status == "ACTIVE",
            Bin.current_fill_percentage >= high_threshold,
        )
    )
    if location_id is not None:
        bin_q = bin_q.filter(Bin.location_id == location_id)
    if waste_type_id is not None:
        bin_q = bin_q.filter(Bin.waste_type_id == waste_type_id)
    if bin_id is not None:
        bin_q = bin_q.filter(Bin.bin_id == bin_id)

    high_fill_bins = [
        BinDetailSummary(
            bin_id=r.bin_id,
            bin_code=r.bin_code,
            location_name=r.location_name,
            waste_type=r.waste_type,
            current_fill_percentage=float(r.current_fill_percentage) if r.current_fill_percentage is not None else None,
            status=r.status,
        )
        for r in bin_q.order_by(Bin.current_fill_percentage.desc()).all()
    ]

    return BinFillAnalytics(
        average_fill_percentage=avg_fill,
        max_fill_percentage=max_fill,
        min_fill_percentage=min_fill,
        total_readings=total_readings,
        high_fill_reading_count=high_readings,
        high_fill_threshold=high_threshold,
        high_fill_bins=high_fill_bins,
    )


def get_operational_alerts(
    db: Session,
    threshold: Optional[float] = None,
) -> List[AlertItem]:
    """
    Derives operational alerts in real-time from existing models without a separate alert table.
    Alert categories: HIGH_FILL_BIN, OVERFLOW_REPORT, DAMAGED_BIN, MISSING_BIN, PENDING_REPORT.
    """
    high_threshold = threshold if threshold is not None else settings.HIGH_FILL_THRESHOLD
    alerts: List[AlertItem] = []

    # 1. High Fill Bins
    high_bins = (
        db.query(
            Bin.bin_id,
            Bin.bin_code,
            Location.name.label("location_name"),
            WasteType.name.label("waste_type_name"),
            Bin.current_fill_percentage,
            Bin.updated_at,
        )
        .join(Location, Bin.location_id == Location.location_id)
        .join(WasteType, Bin.waste_type_id == WasteType.waste_type_id)
        .filter(
            Bin.status == "ACTIVE",
            Bin.current_fill_percentage >= high_threshold,
        )
        .all()
    )
    for b in high_bins:
        sev = "CRITICAL" if (b.current_fill_percentage or 0) >= 95.0 else "WARNING"
        alerts.append(
            AlertItem(
                alert_type="HIGH_FILL_BIN",
                severity=sev,
                title=f"High Bin Fill: {b.bin_code} ({b.current_fill_percentage}%)",
                description=f"Bin {b.bin_code} at {b.location_name} ({b.waste_type_name}) is at {b.current_fill_percentage}% capacity.",
                bin_id=b.bin_id,
                bin_code=b.bin_code,
                location_name=b.location_name,
                waste_type_name=b.waste_type_name,
                related_id=str(b.bin_id),
                observed_at=b.updated_at or datetime.now(timezone.utc),
            )
        )

    # 2. Damaged / Missing Bins
    flagged_bins = (
        db.query(
            Bin.bin_id,
            Bin.bin_code,
            Bin.status,
            Location.name.label("location_name"),
            WasteType.name.label("waste_type_name"),
            Bin.updated_at,
        )
        .join(Location, Bin.location_id == Location.location_id)
        .join(WasteType, Bin.waste_type_id == WasteType.waste_type_id)
        .filter(Bin.status.in_(["DAMAGED", "MISSING"]))
        .all()
    )
    for b in flagged_bins:
        alert_type = f"{b.status}_BIN"
        alerts.append(
            AlertItem(
                alert_type=alert_type,
                severity="WARNING",
                title=f"{b.status.capitalize()} Bin: {b.bin_code}",
                description=f"Bin {b.bin_code} at {b.location_name} is marked as {b.status}.",
                bin_id=b.bin_id,
                bin_code=b.bin_code,
                location_name=b.location_name,
                waste_type_name=b.waste_type_name,
                related_id=str(b.bin_id),
                observed_at=b.updated_at or datetime.now(timezone.utc),
            )
        )

    # 3. Pending Waste Reports
    pending_reports = (
        db.query(
            WasteReport.report_id,
            WasteReport.report_type,
            WasteReport.description,
            WasteReport.created_at,
            Bin.bin_id,
            Bin.bin_code,
            Location.name.label("location_name"),
            WasteType.name.label("waste_type_name"),
        )
        .outerjoin(Bin, WasteReport.bin_id == Bin.bin_id)
        .outerjoin(Location, Bin.location_id == Location.location_id)
        .outerjoin(WasteType, Bin.waste_type_id == WasteType.waste_type_id)
        .filter(WasteReport.status == "PENDING")
        .all()
    )
    for rep in pending_reports:
        if rep.report_type == "OVERFLOWING":
            alert_type = "OVERFLOW_REPORT"
            sev = "CRITICAL"
        else:
            alert_type = "PENDING_REPORT"
            sev = "INFO"

        alerts.append(
            AlertItem(
                alert_type=alert_type,
                severity=sev,
                title=f"Pending Report: {rep.report_type}",
                description=rep.description or f"A report of type {rep.report_type} is awaiting administrative review.",
                bin_id=rep.bin_id,
                bin_code=rep.bin_code,
                location_name=rep.location_name,
                waste_type_name=rep.waste_type_name,
                related_id=str(rep.report_id),
                observed_at=rep.created_at or datetime.now(timezone.utc),
            )
        )

    # Sort alerts by severity (CRITICAL -> WARNING -> INFO) and timestamp desc
    sev_order = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}
    alerts.sort(key=lambda a: (sev_order.get(a.severity, 99), -a.observed_at.timestamp()))

    return alerts


def get_report_analytics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    location_id: Optional[int] = None,
) -> ReportAnalytics:
    """
    Returns analytics on waste reporting volumes, types, locations, and resolution times.
    """
    start_dt, end_dt = _normalize_date_range(start_date, end_date)

    # Status breakdown
    status_query = (
        db.query(WasteReport.status, sa.func.count(WasteReport.report_id))
        .outerjoin(Bin, WasteReport.bin_id == Bin.bin_id)
        .filter(
            WasteReport.created_at >= start_dt,
            WasteReport.created_at < end_dt,
        )
    )
    if location_id is not None:
        status_query = status_query.filter(Bin.location_id == location_id)
    status_counts = dict(status_query.group_by(WasteReport.status).all())

    total_reports = sum(status_counts.values())
    pending_reports = status_counts.get("PENDING", 0)
    in_progress_reports = status_counts.get("IN_PROGRESS", 0)
    resolved_reports = status_counts.get("RESOLVED", 0)
    rejected_reports = status_counts.get("REJECTED", 0)

    # Type breakdown
    type_query = (
        db.query(WasteReport.report_type, sa.func.count(WasteReport.report_id))
        .outerjoin(Bin, WasteReport.bin_id == Bin.bin_id)
        .filter(
            WasteReport.created_at >= start_dt,
            WasteReport.created_at < end_dt,
        )
    )
    if location_id is not None:
        type_query = type_query.filter(Bin.location_id == location_id)
    type_counts = dict(type_query.group_by(WasteReport.report_type).all())

    # Location breakdown
    loc_rows = (
        db.query(
            Location.location_id,
            Location.name.label("location_name"),
            sa.func.count(WasteReport.report_id).label("report_count"),
        )
        .join(Bin, WasteReport.bin_id == Bin.bin_id)
        .join(Location, Bin.location_id == Location.location_id)
        .filter(
            WasteReport.created_at >= start_dt,
            WasteReport.created_at < end_dt,
        )
        .group_by(Location.location_id, Location.name)
        .all()
    )
    reports_by_loc = [
        {
            "location_id": r.location_id,
            "location_name": r.location_name,
            "report_count": r.report_count,
        }
        for r in loc_rows
    ]

    # Average resolution time in hours for resolved reports
    resolved_query = (
        db.query(WasteReport.created_at, WasteReport.resolved_at)
        .outerjoin(Bin, WasteReport.bin_id == Bin.bin_id)
        .filter(
            WasteReport.status == "RESOLVED",
            WasteReport.resolved_at.isnot(None),
            WasteReport.created_at >= start_dt,
            WasteReport.created_at < end_dt,
        )
    )
    if location_id is not None:
        resolved_query = resolved_query.filter(Bin.location_id == location_id)
    resolved_reports_list = resolved_query.all()

    avg_res_hours: Optional[float] = None
    if resolved_reports_list:
        diffs = [
            (r.resolved_at - r.created_at).total_seconds() / 3600.0
            for r in resolved_reports_list
            if r.resolved_at and r.created_at and r.resolved_at >= r.created_at
        ]
        if diffs:
            avg_res_hours = round(sum(diffs) / len(diffs), 2)

    return ReportAnalytics(
        total_reports=total_reports,
        pending_reports=pending_reports,
        in_progress_reports=in_progress_reports,
        resolved_reports=resolved_reports,
        rejected_reports=rejected_reports,
        reports_by_type=type_counts,
        reports_by_location=reports_by_loc,
        average_resolution_time_hours=avg_res_hours,
    )


def get_processing_analytics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    processing_type: Optional[str] = None,
    location_id: Optional[int] = None,
    waste_type_id: Optional[int] = None,
) -> ProcessingAnalytics:
    """
    Returns analytics on recycling and composting output, including basic diversion rate metrics.
    """
    start_dt, end_dt = _normalize_date_range(start_date, end_date)

    query = (
        db.query(
            sa.func.count(ProcessingRecord.processing_id).label("total_records"),
            sa.func.sum(ProcessingRecord.quantity_kg).label("total_proc"),
            sa.func.sum(
                sa.case(
                    (ProcessingRecord.processing_type == "RECYCLING", ProcessingRecord.quantity_kg),
                    else_=0,
                )
            ).label("total_rec"),
            sa.func.sum(
                sa.case(
                    (ProcessingRecord.processing_type == "COMPOSTING", ProcessingRecord.quantity_kg),
                    else_=0,
                )
            ).label("total_comp"),
        )
        .join(CollectionRecord, ProcessingRecord.collection_id == CollectionRecord.collection_id)
        .join(Bin, CollectionRecord.bin_id == Bin.bin_id)
        .filter(
            ProcessingRecord.processed_at >= start_dt,
            ProcessingRecord.processed_at < end_dt,
        )
    )
    if processing_type is not None:
        query = query.filter(ProcessingRecord.processing_type == processing_type)
    if location_id is not None:
        query = query.filter(Bin.location_id == location_id)
    if waste_type_id is not None:
        query = query.filter(Bin.waste_type_id == waste_type_id)

    row = query.first()
    total_records = row.total_records if row else 0
    total_proc = float(row.total_proc) if row and row.total_proc is not None else None
    total_rec = float(row.total_rec) if row and row.total_rec is not None and total_proc is not None else None
    total_comp = float(row.total_comp) if row and row.total_comp is not None and total_proc is not None else None

    # Calculate diversion rate against total collected kg in same scope
    col_query = (
        db.query(sa.func.sum(CollectionRecord.collected_quantity_kg))
        .join(Bin, CollectionRecord.bin_id == Bin.bin_id)
        .filter(
            CollectionRecord.collected_at >= start_dt,
            CollectionRecord.collected_at < end_dt,
        )
    )
    if location_id is not None:
        col_query = col_query.filter(Bin.location_id == location_id)
    if waste_type_id is not None:
        col_query = col_query.filter(Bin.waste_type_id == waste_type_id)

    total_col_sum = col_query.scalar()
    diversion_rate: Optional[float] = None
    if total_col_sum is not None and total_col_sum > 0:
        if total_proc is not None:
            diversion_rate = round((total_proc / float(total_col_sum)) * 100.0, 2)
        else:
            diversion_rate = 0.0

    # Processing by waste type
    wt_rows = (
        db.query(
            WasteType.waste_type_id,
            WasteType.name.label("waste_type_name"),
            sa.func.sum(ProcessingRecord.quantity_kg).label("proc_kg"),
            sa.func.sum(
                sa.case(
                    (ProcessingRecord.processing_type == "RECYCLING", ProcessingRecord.quantity_kg),
                    else_=0,
                )
            ).label("rec_kg"),
            sa.func.sum(
                sa.case(
                    (ProcessingRecord.processing_type == "COMPOSTING", ProcessingRecord.quantity_kg),
                    else_=0,
                )
            ).label("comp_kg"),
        )
        .join(Bin, Bin.waste_type_id == WasteType.waste_type_id)
        .join(CollectionRecord, CollectionRecord.bin_id == Bin.bin_id)
        .join(ProcessingRecord, ProcessingRecord.collection_id == CollectionRecord.collection_id)
        .filter(
            ProcessingRecord.processed_at >= start_dt,
            ProcessingRecord.processed_at < end_dt,
        )
        .group_by(WasteType.waste_type_id, WasteType.name)
        .all()
    )
    by_wt = [
        {
            "waste_type_id": r.waste_type_id,
            "waste_type_name": r.waste_type_name,
            "processed_quantity_kg": float(r.proc_kg) if r.proc_kg is not None else 0.0,
            "recycled_quantity_kg": float(r.rec_kg) if r.rec_kg is not None else 0.0,
            "composted_quantity_kg": float(r.comp_kg) if r.comp_kg is not None else 0.0,
        }
        for r in wt_rows
    ]

    # Processing by location
    loc_rows = (
        db.query(
            Location.location_id,
            Location.name.label("location_name"),
            sa.func.sum(ProcessingRecord.quantity_kg).label("proc_kg"),
            sa.func.sum(
                sa.case(
                    (ProcessingRecord.processing_type == "RECYCLING", ProcessingRecord.quantity_kg),
                    else_=0,
                )
            ).label("rec_kg"),
            sa.func.sum(
                sa.case(
                    (ProcessingRecord.processing_type == "COMPOSTING", ProcessingRecord.quantity_kg),
                    else_=0,
                )
            ).label("comp_kg"),
        )
        .join(Bin, Bin.location_id == Location.location_id)
        .join(CollectionRecord, CollectionRecord.bin_id == Bin.bin_id)
        .join(ProcessingRecord, ProcessingRecord.collection_id == CollectionRecord.collection_id)
        .filter(
            ProcessingRecord.processed_at >= start_dt,
            ProcessingRecord.processed_at < end_dt,
        )
        .group_by(Location.location_id, Location.name)
        .all()
    )
    by_loc = [
        {
            "location_id": r.location_id,
            "location_name": r.location_name,
            "processed_quantity_kg": float(r.proc_kg) if r.proc_kg is not None else 0.0,
            "recycled_quantity_kg": float(r.rec_kg) if r.rec_kg is not None else 0.0,
            "composted_quantity_kg": float(r.comp_kg) if r.comp_kg is not None else 0.0,
        }
        for r in loc_rows
    ]

    return ProcessingAnalytics(
        total_processing_records=total_records,
        total_processed_quantity_kg=total_proc,
        total_recycled_quantity_kg=total_rec,
        total_composted_quantity_kg=total_comp,
        diversion_rate=diversion_rate,
        processing_by_waste_type=by_wt,
        processing_by_location=by_loc,
    )


def get_participation_analytics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> ParticipationAnalytics:
    """
    Returns analytics on student campus participation rates based on actual waste activity.
    """
    start_dt, end_dt = _normalize_date_range(start_date, end_date)

    student_role = db.query(Role).filter(Role.role_name == "STUDENT").first()
    student_role_id = student_role.role_id if student_role else None

    total_active_students = (
        db.query(sa.func.count(User.user_id))
        .filter(User.role_id == student_role_id, User.is_active == True)  # noqa: E712
        .scalar()
        or 0
        if student_role_id
        else 0
    )

    # Students with at least 1 disposal
    students_with_disp = (
        db.query(sa.func.count(sa.distinct(DisposalRecord.user_id)))
        .join(User, DisposalRecord.user_id == User.user_id)
        .filter(
            User.role_id == student_role_id,
            DisposalRecord.recorded_at >= start_dt,
            DisposalRecord.recorded_at < end_dt,
        )
        .scalar()
        or 0
        if student_role_id
        else 0
    )

    # Unique participating students (disposal or report)
    disp_users_stmt = (
        db.query(DisposalRecord.user_id.label("uid"))
        .join(User, DisposalRecord.user_id == User.user_id)
        .filter(
            User.role_id == student_role_id,
            DisposalRecord.recorded_at >= start_dt,
            DisposalRecord.recorded_at < end_dt,
        )
    )
    report_users_stmt = (
        db.query(WasteReport.user_id.label("uid"))
        .join(User, WasteReport.user_id == User.user_id)
        .filter(
            User.role_id == student_role_id,
            WasteReport.created_at >= start_dt,
            WasteReport.created_at < end_dt,
        )
    )
    union_users = disp_users_stmt.union(report_users_stmt).subquery()
    unique_participating = db.query(sa.func.count(union_users.c.uid)).scalar() or 0

    disposals_count = (
        db.query(sa.func.count(DisposalRecord.disposal_id))
        .filter(
            DisposalRecord.recorded_at >= start_dt,
            DisposalRecord.recorded_at < end_dt,
        )
        .scalar()
        or 0
    )

    reports_sub = (
        db.query(sa.func.count(WasteReport.report_id))
        .filter(
            WasteReport.created_at >= start_dt,
            WasteReport.created_at < end_dt,
        )
        .scalar()
        or 0
    )

    reports_res = (
        db.query(sa.func.count(WasteReport.report_id))
        .filter(
            WasteReport.status == "RESOLVED",
            WasteReport.created_at >= start_dt,
            WasteReport.created_at < end_dt,
        )
        .scalar()
        or 0
    )

    participation_rate: Optional[float] = None
    if total_active_students > 0:
        participation_rate = round(
            (students_with_disp / total_active_students) * 100.0, 2
        )

    return ParticipationAnalytics(
        total_active_students=total_active_students,
        students_with_at_least_one_disposal=students_with_disp,
        unique_participating_students=unique_participating,
        disposal_records_count=disposals_count,
        reports_submitted_count=reports_sub,
        reports_resolved_count=reports_res,
        participation_rate=participation_rate,
    )


def get_gamification_analytics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> GamificationAnalytics:
    """
    Returns aggregated metrics on points earned, redemptions, and popular rewards.
    """
    start_dt, end_dt = _normalize_date_range(start_date, end_date)

    earned_agg = (
        db.query(
            sa.func.sum(PointTransaction.points).label("total_earned"),
            sa.func.count(PointTransaction.transaction_id).label("earn_count"),
            sa.func.count(sa.distinct(PointTransaction.user_id)).label("unique_students"),
        )
        .filter(
            PointTransaction.points > 0,
            PointTransaction.created_at >= start_dt,
            PointTransaction.created_at < end_dt,
        )
        .first()
    )

    total_earned = int(earned_agg.total_earned) if earned_agg and earned_agg.total_earned is not None else 0
    earn_count = earned_agg.earn_count if earned_agg else 0
    unique_students = earned_agg.unique_students if earned_agg else 0

    points_redeemed = (
        db.query(sa.func.sum(sa.func.abs(PointTransaction.points)))
        .filter(
            PointTransaction.points < 0,
            PointTransaction.created_at >= start_dt,
            PointTransaction.created_at < end_dt,
        )
        .scalar()
        or 0
    )

    redemptions_count = (
        db.query(sa.func.count(RewardRedemption.redemption_id))
        .filter(
            RewardRedemption.created_at >= start_dt,
            RewardRedemption.created_at < end_dt,
        )
        .scalar()
        or 0
    )

    # Points earned by source type
    action_rows = (
        db.query(
            PointTransaction.source_type,
            sa.func.sum(PointTransaction.points).label("pts"),
        )
        .filter(
            PointTransaction.points > 0,
            PointTransaction.created_at >= start_dt,
            PointTransaction.created_at < end_dt,
        )
        .group_by(PointTransaction.source_type)
        .all()
    )
    points_by_action = {r.source_type: int(r.pts) for r in action_rows}

    # Most redeemed rewards
    reward_rows = (
        db.query(
            Reward.reward_id,
            Reward.name.label("reward_title"),
            sa.func.count(RewardRedemption.redemption_id).label("redemption_count"),
            sa.func.sum(RewardRedemption.points_spent).label("total_points_spent"),
        )
        .join(RewardRedemption, RewardRedemption.reward_id == Reward.reward_id)
        .filter(
            RewardRedemption.created_at >= start_dt,
            RewardRedemption.created_at < end_dt,
        )
        .group_by(Reward.reward_id, Reward.name)
        .order_by(sa.func.count(RewardRedemption.redemption_id).desc())
        .limit(10)
        .all()
    )
    most_redeemed = [
        {
            "reward_id": r.reward_id,
            "reward_title": r.reward_title,
            "redemption_count": r.redemption_count,
            "total_points_spent": int(r.total_points_spent) if r.total_points_spent is not None else 0,
        }
        for r in reward_rows
    ]

    return GamificationAnalytics(
        total_points_earned=total_earned,
        total_points_redeemed=int(points_redeemed),
        earning_transactions_count=earn_count,
        reward_redemptions_count=redemptions_count,
        unique_participating_students=unique_students,
        points_earned_by_action=points_by_action,
        most_redeemed_rewards=most_redeemed,
    )


def get_prediction_analytics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    bin_id: Optional[uuid.UUID] = None,
) -> PredictionAnalytics:
    """
    Returns analytical evaluation of generated bin fill predictions.
    Preserves chronological integrity and does not compare against unobserved future states.
    """
    start_dt, end_dt = _normalize_date_range(start_date, end_date)

    agg = (
        db.query(
            sa.func.count(FillPrediction.prediction_id).label("total_preds"),
            sa.func.avg(FillPrediction.predicted_fill_percentage).label("avg_fill"),
            sa.func.max(FillPrediction.predicted_fill_percentage).label("max_fill"),
            sa.func.sum(
                sa.case(
                    (FillPrediction.predicted_fill_percentage >= settings.HIGH_FILL_THRESHOLD, 1),
                    else_=0,
                )
            ).label("high_preds"),
        )
        .filter(
            FillPrediction.created_at >= start_dt,
            FillPrediction.created_at < end_dt,
        )
    )
    if bin_id is not None:
        agg = agg.filter(FillPrediction.bin_id == bin_id)

    row = agg.first()
    total_preds = row.total_preds if row else 0
    avg_fill = round(float(row.avg_fill), 2) if row and row.avg_fill is not None else None
    max_fill = float(row.max_fill) if row and row.max_fill is not None else None
    high_preds = int(row.high_preds) if row and row.high_preds is not None else 0

    # Predictions by model version
    mv_query = (
        db.query(
            FillPrediction.model_version,
            sa.func.count(FillPrediction.prediction_id),
        )
        .filter(
            FillPrediction.created_at >= start_dt,
            FillPrediction.created_at < end_dt,
        )
    )
    if bin_id is not None:
        mv_query = mv_query.filter(FillPrediction.bin_id == bin_id)
    by_version = dict(mv_query.group_by(FillPrediction.model_version).all())

    # Predictions by bin
    bin_preds = (
        db.query(
            Bin.bin_id,
            Bin.bin_code,
            Location.name.label("location_name"),
            sa.func.count(FillPrediction.prediction_id).label("pred_count"),
            sa.func.avg(FillPrediction.predicted_fill_percentage).label("avg_fill"),
        )
        .join(Bin, FillPrediction.bin_id == Bin.bin_id)
        .join(Location, Bin.location_id == Location.location_id)
        .filter(
            FillPrediction.created_at >= start_dt,
            FillPrediction.created_at < end_dt,
        )
    )
    if bin_id is not None:
        bin_preds = bin_preds.filter(FillPrediction.bin_id == bin_id)

    bin_rows = (
        bin_preds.group_by(Bin.bin_id, Bin.bin_code, Location.name)
        .order_by(sa.func.count(FillPrediction.prediction_id).desc())
        .limit(10)
        .all()
    )
    by_bin = [
        {
            "bin_id": str(r.bin_id),
            "bin_code": r.bin_code,
            "location_name": r.location_name,
            "prediction_count": r.pred_count,
            "average_predicted_fill": round(float(r.avg_fill), 2) if r.avg_fill is not None else None,
        }
        for r in bin_rows
    ]

    return PredictionAnalytics(
        total_predictions=total_preds,
        average_predicted_fill=avg_fill,
        max_predicted_fill=max_fill,
        high_fill_predictions_count=high_preds,
        predictions_by_model_version=by_version,
        predictions_by_bin=by_bin,
    )


def get_classification_analytics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> ClassificationAnalytics:
    """
    Returns analytics on AI waste classifications (distribution, confidence levels, model versions).
    Note: Accuracy is out of scope without labeled ground-truth data.
    """
    start_dt, end_dt = _normalize_date_range(start_date, end_date)

    agg = (
        db.query(
            sa.func.count(WasteClassification.classification_id).label("total_classes"),
            sa.func.avg(WasteClassification.confidence_score).label("avg_conf"),
            sa.func.sum(
                sa.case(
                    (WasteClassification.confidence_score < 0.60, 1),
                    else_=0,
                )
            ).label("low_conf"),
        )
        .filter(
            WasteClassification.created_at >= start_dt,
            WasteClassification.created_at < end_dt,
        )
        .first()
    )

    total_classes = agg.total_classes if agg else 0
    avg_conf = round(float(agg.avg_conf), 4) if agg and agg.avg_conf is not None else None
    low_conf = int(agg.low_conf) if agg and agg.low_conf is not None else 0

    # Classifications by waste type name
    wt_class_rows = (
        db.query(
            WasteType.name,
            sa.func.count(WasteClassification.classification_id),
        )
        .join(WasteType, WasteClassification.predicted_waste_type_id == WasteType.waste_type_id)
        .filter(
            WasteClassification.created_at >= start_dt,
            WasteClassification.created_at < end_dt,
        )
        .group_by(WasteType.name)
        .all()
    )
    by_type = dict(wt_class_rows)

    by_version = dict(
        db.query(
            WasteClassification.model_version,
            sa.func.count(WasteClassification.classification_id),
        )
        .filter(
            WasteClassification.created_at >= start_dt,
            WasteClassification.created_at < end_dt,
        )
        .group_by(WasteClassification.model_version)
        .all()
    )

    return ClassificationAnalytics(
        total_classifications=total_classes,
        average_confidence=avg_conf,
        low_confidence_count=low_conf,
        classifications_by_waste_type=by_type,
        classifications_by_model_version=by_version,
    )

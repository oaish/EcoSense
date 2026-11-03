import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import User
from app.schemas.analytics import (
    AlertItem,
    AnalyticsSummary,
    BinFillAnalytics,
    ClassificationAnalytics,
    CollectionAnalytics,
    GamificationAnalytics,
    LocationMetric,
    ParticipationAnalytics,
    PredictionAnalytics,
    ProcessingAnalytics,
    ReportAnalytics,
    TrendAnalytics,
    WasteTypeMetric,
)
from app.services import analytics_service

router = APIRouter()


@router.get(
    "/summary",
    response_model=AnalyticsSummary,
    summary="Get campus-wide waste analytics summary",
    description="Returns high-level summary cards across operations, participation, gamification, and predictions.",
)
def get_analytics_summary_endpoint(
    start_date: Optional[datetime] = Query(
        None,
        description="Inclusive start timestamp (UTC). Defaults to 30 days prior.",
    ),
    end_date: Optional[datetime] = Query(
        None,
        description="Exclusive end timestamp (UTC). Defaults to current time.",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> AnalyticsSummary:
    return analytics_service.get_analytics_summary(
        db=db, start_date=start_date, end_date=end_date
    )


@router.get(
    "/waste-types",
    response_model=List[WasteTypeMetric],
    summary="Get waste analytics grouped by waste type",
    description="Returns disposal, collection, and processing volumes categorized by waste type.",
)
def get_waste_type_analytics_endpoint(
    start_date: Optional[datetime] = Query(None, description="Inclusive start timestamp"),
    end_date: Optional[datetime] = Query(None, description="Exclusive end timestamp"),
    location_id: Optional[int] = Query(None, description="Filter by physical campus location"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> List[WasteTypeMetric]:
    return analytics_service.get_waste_type_analytics(
        db=db, start_date=start_date, end_date=end_date, location_id=location_id
    )


@router.get(
    "/locations",
    response_model=List[LocationMetric],
    summary="Get waste analytics grouped by location",
    description="Returns metrics on bin counts, disposal volume, collection mass, and average fill per location.",
)
def get_location_analytics_endpoint(
    start_date: Optional[datetime] = Query(None, description="Inclusive start timestamp"),
    end_date: Optional[datetime] = Query(None, description="Exclusive end timestamp"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> List[LocationMetric]:
    return analytics_service.get_location_analytics(
        db=db, start_date=start_date, end_date=end_date
    )


@router.get(
    "/trends",
    response_model=TrendAnalytics,
    summary="Get time-series waste trends",
    description="Returns temporal trend points aggregated by day, week, or month.",
)
def get_trend_analytics_endpoint(
    start_date: Optional[datetime] = Query(None, description="Inclusive start timestamp"),
    end_date: Optional[datetime] = Query(None, description="Exclusive end timestamp"),
    granularity: str = Query(
        "day",
        pattern="^(day|week|month)$",
        description="Aggregation time bucket ('day', 'week', 'month')",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> TrendAnalytics:
    return analytics_service.get_trend_analytics(
        db=db, start_date=start_date, end_date=end_date, granularity=granularity
    )


@router.get(
    "/collections",
    response_model=CollectionAnalytics,
    summary="Get collection operational metrics",
    description="Returns aggregated metrics on collections, fill reductions, and frequently serviced bins.",
)
def get_collection_analytics_endpoint(
    start_date: Optional[datetime] = Query(None, description="Inclusive start timestamp"),
    end_date: Optional[datetime] = Query(None, description="Exclusive end timestamp"),
    location_id: Optional[int] = Query(None, description="Filter by location"),
    bin_id: Optional[uuid.UUID] = Query(None, description="Filter by specific bin ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> CollectionAnalytics:
    return analytics_service.get_collection_analytics(
        db=db,
        start_date=start_date,
        end_date=end_date,
        location_id=location_id,
        bin_id=bin_id,
    )


@router.get(
    "/bin-fill",
    response_model=BinFillAnalytics,
    summary="Get bin fill statistics and high-fill list",
    description="Returns fill percentage statistics and currently high-fill bins above threshold.",
)
def get_bin_fill_analytics_endpoint(
    start_date: Optional[datetime] = Query(None, description="Inclusive start timestamp"),
    end_date: Optional[datetime] = Query(None, description="Exclusive end timestamp"),
    location_id: Optional[int] = Query(None, description="Filter by location"),
    waste_type_id: Optional[int] = Query(None, description="Filter by waste type"),
    bin_id: Optional[uuid.UUID] = Query(None, description="Filter by specific bin ID"),
    threshold: Optional[float] = Query(
        None, ge=0.0, le=100.0, description="Custom high-fill percentage threshold"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> BinFillAnalytics:
    return analytics_service.get_bin_fill_analytics(
        db=db,
        start_date=start_date,
        end_date=end_date,
        location_id=location_id,
        waste_type_id=waste_type_id,
        bin_id=bin_id,
        threshold=threshold,
    )


@router.get(
    "/alerts",
    response_model=List[AlertItem],
    summary="Get operational alerts derived from current system state",
    description="Returns real-time derived alerts (high fill, damaged/missing bins, overflow reports) without dedicated alert tables.",
)
def get_operational_alerts_endpoint(
    threshold: Optional[float] = Query(
        None, ge=0.0, le=100.0, description="Custom high-fill threshold"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> List[AlertItem]:
    return analytics_service.get_operational_alerts(db=db, threshold=threshold)


@router.get(
    "/reports",
    response_model=ReportAnalytics,
    summary="Get waste report breakdown and resolution times",
    description="Returns breakdown of report statuses, types, locations, and average resolution time.",
)
def get_report_analytics_endpoint(
    start_date: Optional[datetime] = Query(None, description="Inclusive start timestamp"),
    end_date: Optional[datetime] = Query(None, description="Exclusive end timestamp"),
    location_id: Optional[int] = Query(None, description="Filter by location"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> ReportAnalytics:
    return analytics_service.get_report_analytics(
        db=db, start_date=start_date, end_date=end_date, location_id=location_id
    )


@router.get(
    "/processing",
    response_model=ProcessingAnalytics,
    summary="Get recycling and composting processing analytics",
    description="Returns quantities processed, recycled, composted, and campus diversion rate.",
)
def get_processing_analytics_endpoint(
    start_date: Optional[datetime] = Query(None, description="Inclusive start timestamp"),
    end_date: Optional[datetime] = Query(None, description="Exclusive end timestamp"),
    processing_type: Optional[str] = Query(
        None,
        pattern="^(RECYCLING|COMPOSTING)$",
        description="Filter by processing type",
    ),
    location_id: Optional[int] = Query(None, description="Filter by origin location"),
    waste_type_id: Optional[int] = Query(None, description="Filter by waste type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> ProcessingAnalytics:
    return analytics_service.get_processing_analytics(
        db=db,
        start_date=start_date,
        end_date=end_date,
        processing_type=processing_type,
        location_id=location_id,
        waste_type_id=waste_type_id,
    )


@router.get(
    "/participation",
    response_model=ParticipationAnalytics,
    summary="Get student participation and disposal engagement rate",
    description="Returns statistics on student activity, active student counts, and campus engagement rate.",
)
def get_participation_analytics_endpoint(
    start_date: Optional[datetime] = Query(None, description="Inclusive start timestamp"),
    end_date: Optional[datetime] = Query(None, description="Exclusive end timestamp"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> ParticipationAnalytics:
    return analytics_service.get_participation_analytics(
        db=db, start_date=start_date, end_date=end_date
    )


@router.get(
    "/gamification",
    response_model=GamificationAnalytics,
    summary="Get gamification points and reward redemption analytics",
    description="Returns aggregated points earned, points redeemed, and top redeemed rewards.",
)
def get_gamification_analytics_endpoint(
    start_date: Optional[datetime] = Query(None, description="Inclusive start timestamp"),
    end_date: Optional[datetime] = Query(None, description="Exclusive end timestamp"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> GamificationAnalytics:
    return analytics_service.get_gamification_analytics(
        db=db, start_date=start_date, end_date=end_date
    )


@router.get(
    "/predictions",
    response_model=PredictionAnalytics,
    summary="Get fill prediction model analytics",
    description="Returns prediction counts, average forecast fills, high-fill forecast counts, and model version distributions.",
)
def get_prediction_analytics_endpoint(
    start_date: Optional[datetime] = Query(None, description="Inclusive start timestamp"),
    end_date: Optional[datetime] = Query(None, description="Exclusive end timestamp"),
    bin_id: Optional[uuid.UUID] = Query(None, description="Filter by specific bin ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> PredictionAnalytics:
    return analytics_service.get_prediction_analytics(
        db=db, start_date=start_date, end_date=end_date, bin_id=bin_id
    )


@router.get(
    "/classifications",
    response_model=ClassificationAnalytics,
    summary="Get AI classification analytics",
    description="Returns AI classification volume, confidence distribution, low-confidence counts, and predicted waste categories.",
)
def get_classification_analytics_endpoint(
    start_date: Optional[datetime] = Query(None, description="Inclusive start timestamp"),
    end_date: Optional[datetime] = Query(None, description="Exclusive end timestamp"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> ClassificationAnalytics:
    return analytics_service.get_classification_analytics(
        db=db, start_date=start_date, end_date=end_date
    )

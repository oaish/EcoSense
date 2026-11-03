from app.schemas.auth import LoginRequest, TokenPayload, TokenResponse
from app.schemas.bin import BinCreate, BinQRRead, BinRead, BinUpdate
from app.schemas.classification import ClassificationCreate, ClassificationRead
from app.schemas.collection import CollectionCreate, CollectionRead
from app.schemas.disposal import DisposalCreate, DisposalRead
from app.schemas.fill_reading import (
    VALID_FILL_SOURCES,
    FillReadingCreate,
    FillReadingRead,
)
from app.schemas.gamification import (
    PointAdjustmentCreate,
    PointBalanceRead,
    PointRuleRead,
    PointTransactionRead,
    RewardCreate,
    RewardRead,
    RewardRedemptionRead,
    RewardUpdate,
)
from app.schemas.location import LocationCreate, LocationRead, LocationSummary, LocationUpdate
from app.schemas.prediction import PredictionRead, PredictionRequest
from app.schemas.processing import ProcessingCreate, ProcessingRead
from app.schemas.report import (
    VALID_REPORT_STATUSES,
    VALID_REPORT_TYPES,
    ReportCreate,
    ReportRead,
    ReportUpdate,
)
from app.schemas.user import AdminTestResponse, RoleRead, UserCreate, UserRead, UserSummary
from app.schemas.attendance import (
    AdminAttendanceOverview,
    AttendanceCheckInRequest,
    AttendanceCheckOutRequest,
    AttendanceRead,
    CollectorShiftSummary,
)
from app.schemas.task import (
    TaskCreate,
    TaskDelegateReportRequest,
    TaskListResponse,
    TaskRead,
    TaskReassignRequest,
    TaskStatusUpdate,
    VALID_TASK_PRIORITIES,
    VALID_TASK_STATUSES,
    VALID_TASK_TYPES,
)
from app.schemas.waste_type import (
    WasteTypeCreate,
    WasteTypeRead,
    WasteTypeSummary,
    WasteTypeUpdate,
)

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

__all__ = [
    "LoginRequest",
    "TokenPayload",
    "TokenResponse",
    "RoleRead",
    "UserCreate",
    "UserRead",
    "UserSummary",
    "AdminTestResponse",
    "LocationCreate",
    "LocationUpdate",
    "LocationRead",
    "LocationSummary",
    "WasteTypeCreate",
    "WasteTypeUpdate",
    "WasteTypeRead",
    "WasteTypeSummary",
    "BinCreate",
    "BinUpdate",
    "BinRead",
    "BinQRRead",
    "DisposalCreate",
    "DisposalRead",
    "ReportCreate",
    "ReportUpdate",
    "ReportRead",
    "VALID_REPORT_TYPES",
    "VALID_REPORT_STATUSES",
    "FillReadingCreate",
    "FillReadingRead",
    "VALID_FILL_SOURCES",
    "CollectionCreate",
    "CollectionRead",
    "ClassificationCreate",
    "ClassificationRead",
    "PredictionRequest",
    "PredictionRead",
    "ProcessingCreate",
    "ProcessingRead",
    "PointBalanceRead",
    "PointTransactionRead",
    "PointAdjustmentCreate",
    "PointRuleRead",
    "RewardCreate",
    "RewardUpdate",
    "RewardRead",
    "RewardRedemptionRead",
    "AnalyticsSummary",
    "SummaryMetrics",
    "OperationalMetrics",
    "ParticipationMetrics",
    "GamificationMetrics",
    "PredictionMetrics",
    "WasteTypeMetric",
    "LocationMetric",
    "TrendPoint",
    "TrendAnalytics",
    "CollectionAnalytics",
    "BinDetailSummary",
    "BinFillAnalytics",
    "AlertItem",
    "ReportAnalytics",
    "ProcessingAnalytics",
    "ParticipationAnalytics",
    "GamificationAnalytics",
    "PredictionAnalytics",
    "ClassificationAnalytics",
]





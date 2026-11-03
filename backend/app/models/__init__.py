from app.models.attendance import CollectorAttendance
from app.models.base import Base
from app.models.bin import Bin
from app.models.classification import WasteClassification
from app.models.collection import CollectionRecord
from app.models.device_token import DeviceToken
from app.models.disposal import DisposalRecord
from app.models.fill_reading import BinFillReading
from app.models.gamification import PointRule, PointTransaction, Reward, RewardRedemption
from app.models.location import Location
from app.models.notification import TaskNotification
from app.models.prediction import FillPrediction
from app.models.processing import ProcessingRecord
from app.models.report import WasteReport
from app.models.role import Role
from app.models.task import CollectionTask
from app.models.user import User
from app.models.waste_type import WasteType

__all__ = [
    "Base",
    "Role",
    "User",
    "Location",
    "WasteType",
    "Bin",
    "DisposalRecord",
    "WasteReport",
    "BinFillReading",
    "CollectionRecord",
    "WasteClassification",
    "FillPrediction",
    "ProcessingRecord",
    "PointTransaction",
    "PointRule",
    "Reward",
    "RewardRedemption",
    "CollectorAttendance",
    "CollectionTask",
    "TaskNotification",
    "DeviceToken",
]





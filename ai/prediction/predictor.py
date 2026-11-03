from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

from ai.prediction.features import BinFillFeatures


@dataclass
class FillPredictionResult:
    """Standard prediction result returned by a fill level predictor."""

    predicted_fill_percentage: float
    prediction_timestamp: datetime
    target_timestamp: datetime
    model_version: str
    confidence_score: Optional[float] = None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseFillPredictor(ABC):
    """Abstract Base Class for Bin Fill Level Forecasting Models."""

    @abstractmethod
    def predict(
        self,
        features: BinFillFeatures,
        prediction_timestamp: datetime,
        target_timestamp: datetime,
    ) -> FillPredictionResult:
        """Forecast bin fill percentage at target timestamp given current features.

        Args:
            features: Extracted BinFillFeatures.
            prediction_timestamp: Time at which prediction was requested.
            target_timestamp: Future time horizon being predicted.

        Returns:
            FillPredictionResult: Output containing predicted fill %, bounds, and version.
        """
        pass

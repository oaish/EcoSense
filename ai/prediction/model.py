from datetime import datetime
from typing import Optional

from ai.prediction.config import default_prediction_config
from ai.prediction.features import BinFillFeatures
from ai.prediction.predictor import BaseFillPredictor, FillPredictionResult


class BaselineFillPredictor(BaseFillPredictor):
    """Development and baseline fill predictor.

    Uses recent accumulation rate extrapolation:
    predicted_fill = clamp(current_fill + (fill_rate_per_hour * horizon_hours), 0.0, 100.0)

    Provides deterministic, fast, interpretable forecasts suitable as a benchmark
    against which future advanced regression and ML models can be compared.
    """

    def __init__(self, model_version: Optional[str] = None) -> None:
        self.model_version = model_version or default_prediction_config.model_version

    def predict(
        self,
        features: BinFillFeatures,
        prediction_timestamp: datetime,
        target_timestamp: datetime,
    ) -> FillPredictionResult:
        # Calculate linear progression
        accumulation_delta = features.fill_rate_per_hour * features.horizon_hours
        raw_prediction = features.current_fill_percentage + accumulation_delta

        # Physical clamping to strictly guarantee 0.0 <= predicted_fill <= 100.0
        predicted_fill = max(0.0, min(100.0, round(raw_prediction, 2)))

        # Meaningful uncertainty interval
        margin = 5.0 if features.recent_readings_count >= 5 else 8.0
        lower_bound = max(0.0, round(predicted_fill - margin, 2))
        upper_bound = min(100.0, round(predicted_fill + margin, 2))

        confidence = 0.85 if features.recent_readings_count >= 5 else 0.70

        return FillPredictionResult(
            predicted_fill_percentage=predicted_fill,
            prediction_timestamp=prediction_timestamp,
            target_timestamp=target_timestamp,
            model_version=self.model_version,
            confidence_score=confidence,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            metadata={
                "is_baseline": True,
                "fill_rate_per_hour": round(features.fill_rate_per_hour, 3),
                "horizon_hours": features.horizon_hours,
            },
        )

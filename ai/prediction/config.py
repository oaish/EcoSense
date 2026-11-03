from dataclasses import dataclass


@dataclass(frozen=True)
class PredictionConfig:
    """Configuration settings for the AI Waste Generation / Bin Fill Prediction subsystem."""

    default_horizon_minutes: int = 120
    min_prediction_readings: int = 3
    model_version: str = "baseline-v1"


default_prediction_config = PredictionConfig()

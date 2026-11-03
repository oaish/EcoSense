from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class ClassifierConfig:
    """Configuration settings for the AI Waste Classification subsystem."""

    model_version: str = "v1.0-mock"
    confidence_threshold: float = 0.70
    supported_classes: List[str] = field(
        default_factory=lambda: [
            "WET_ORGANIC",
            "DRY_RECYCLABLE",
            "PAPER",
            "METAL",
            "E_WASTE",
            "GARDEN",
        ]
    )


default_classifier_config = ClassifierConfig()

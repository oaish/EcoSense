from ai.classification.classifier import BaseWasteClassifier, ClassificationPrediction
from ai.classification.config import ClassifierConfig, default_classifier_config
from ai.classification.model import MockWasteClassifier
from ai.classification.preprocessing import ImageValidationError, validate_image_reference

try:
    from ai.classification.fastai_model import FastAIWasteClassifier
except ImportError:
    FastAIWasteClassifier = None  # type: ignore[assignment,misc]

__all__ = [
    "BaseWasteClassifier",
    "ClassificationPrediction",
    "ClassifierConfig",
    "default_classifier_config",
    "MockWasteClassifier",
    "FastAIWasteClassifier",
    "ImageValidationError",
    "validate_image_reference",
]

import hashlib
from typing import Optional

from ai.classification.classifier import BaseWasteClassifier, ClassificationPrediction
from ai.classification.config import default_classifier_config
from ai.classification.preprocessing import validate_image_reference


class MockWasteClassifier(BaseWasteClassifier):
    """Development and testing mock classifier.

    Provides deterministic, fast, offline waste classification without requiring
    heavy ML runtime dependencies or downloading large pre-trained weights.
    Clearly designated as a development-only mock.
    """

    def __init__(
        self,
        model_version: Optional[str] = None,
        confidence_threshold: Optional[float] = None,
    ) -> None:
        self.model_version = model_version or default_classifier_config.model_version
        self.confidence_threshold = (
            confidence_threshold
            if confidence_threshold is not None
            else default_classifier_config.confidence_threshold
        )

    def classify(self, image_input: str) -> ClassificationPrediction:
        """Classify waste item deterministically based on image reference string or keywords."""
        sanitized = validate_image_reference(image_input)
        lower_input = sanitized.lower()

        # Rule-based deterministic keyword matching for reliable automated test suites
        if any(kw in lower_input for kw in ("invalid_class", "alien_waste", "unmapped")):
            return ClassificationPrediction(
                predicted_class="UNKNOWN_UNMAPPED_WASTE",
                confidence_score=0.99,
                model_version=self.model_version,
                metadata={"is_mock": True, "note": "Development mock classifier - unmapped class test"},
            )

        if any(kw in lower_input for kw in ("low_conf", "blurry", "uncertain", "unknown")):
            return ClassificationPrediction(
                predicted_class="DRY_RECYCLABLE",
                confidence_score=0.51,
                model_version=self.model_version,
                metadata={"is_mock": True, "note": "Development mock classifier - low confidence test"},
            )

        if any(kw in lower_input for kw in ("wet", "organic", "food", "banana", "apple", "compost")):
            return ClassificationPrediction(
                predicted_class="WET_ORGANIC",
                confidence_score=0.95,
                model_version=self.model_version,
                metadata={"is_mock": True, "note": "Development mock classifier"},
            )

        if any(kw in lower_input for kw in ("plastic", "bottle", "dry", "recyclable", "can_recycle", "container")):
            return ClassificationPrediction(
                predicted_class="DRY_RECYCLABLE",
                confidence_score=0.94,
                model_version=self.model_version,
                metadata={"is_mock": True, "note": "Development mock classifier"},
            )

        if any(kw in lower_input for kw in ("paper", "cardboard", "box", "newspaper", "book", "document")):
            return ClassificationPrediction(
                predicted_class="PAPER",
                confidence_score=0.92,
                model_version=self.model_version,
                metadata={"is_mock": True, "note": "Development mock classifier"},
            )

        if any(kw in lower_input for kw in ("metal", "can", "tin", "aluminum", "copper", "iron")):
            return ClassificationPrediction(
                predicted_class="METAL",
                confidence_score=0.91,
                model_version=self.model_version,
                metadata={"is_mock": True, "note": "Development mock classifier"},
            )

        if any(kw in lower_input for kw in ("electronic", "ewaste", "e_waste", "battery", "circuit", "cable", "phone")):
            return ClassificationPrediction(
                predicted_class="E_WASTE",
                confidence_score=0.96,
                model_version=self.model_version,
                metadata={"is_mock": True, "note": "Development mock classifier"},
            )

        if any(kw in lower_input for kw in ("garden", "leaf", "leaves", "grass", "branch", "flower", "tree")):
            return ClassificationPrediction(
                predicted_class="GARDEN",
                confidence_score=0.89,
                model_version=self.model_version,
                metadata={"is_mock": True, "note": "Development mock classifier"},
            )

        # Stable hash fallback to ensure repeatable, deterministic outputs for arbitrary strings
        hash_val = int(hashlib.sha256(lower_input.encode("utf-8")).hexdigest(), 16)
        classes = default_classifier_config.supported_classes
        chosen_class = classes[hash_val % len(classes)]
        # Generate confidence between 0.75 and 0.98 deterministically
        confidence = 0.75 + ((hash_val % 230) / 1000.0)

        return ClassificationPrediction(
            predicted_class=chosen_class,
            confidence_score=round(confidence, 4),
            model_version=self.model_version,
            metadata={"is_mock": True, "note": "Development mock classifier fallback"},
        )

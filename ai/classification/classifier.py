from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ClassificationPrediction:
    """Standard output prediction dataclass returned by any waste classifier."""

    predicted_class: str
    confidence_score: float
    model_version: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseWasteClassifier(ABC):
    """Abstract Base Class for Waste Classification Models.

    All concrete model implementations (Mock, ONNX, PyTorch, TensorRT, etc.)
    must adhere to this interface to ensure strict decoupling from the backend services.
    """

    @abstractmethod
    def classify(self, image_input: str) -> ClassificationPrediction:
        """Classify a waste item given an image reference or path.

        Args:
            image_input: Validated URI, local path, or identifier for the image.

        Returns:
            ClassificationPrediction: Prediction object containing class, confidence,
                                      and model version.
        """
        pass

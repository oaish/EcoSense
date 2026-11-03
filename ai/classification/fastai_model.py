import base64
import io
import logging
import pathlib
import platform
from pathlib import Path
from typing import Any, Dict, Optional, Union
from urllib.request import Request, urlopen

from PIL import Image

from ai.classification.classifier import BaseWasteClassifier, ClassificationPrediction
from ai.classification.preprocessing import ImageValidationError, validate_image_reference

logger = logging.getLogger(__name__)

# Windows compatibility patch: models trained on POSIX use PosixPath in their pickle graph
if platform.system() == "Windows":
    pathlib.PosixPath = pathlib.WindowsPath

# Mapping from FastAI waste_classifier_v2 vocabulary to EcoSense campus waste categories
FASTAI_TO_ECOSENSE_CLASS_MAP: Dict[str, str] = {
    "organic": "WET_ORGANIC",
    "plastic": "DRY_RECYCLABLE",
    "glass": "DRY_RECYCLABLE",
    "metal": "METAL",
    "paper": "PAPER",
    "cardboard": "PAPER",
    "e-waste": "E_WASTE",
    "textile": "DRY_RECYCLABLE",
}

DEFAULT_MODEL_PATH = "ai/models/waste_classifier_v2.pkl"
DEFAULT_MODEL_VERSION = "v2.0-fastai"


class FastAIWasteClassifier(BaseWasteClassifier):
    """Production Waste Classifier utilizing a pre-trained FastAI / PyTorch vision learner."""

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        model_version: Optional[str] = None,
        confidence_threshold: float = 0.70,
    ) -> None:
        from fastai.vision.all import load_learner

        resolved_path = Path(model_path or DEFAULT_MODEL_PATH)
        if not resolved_path.is_absolute():
            # Resolve relative to current working directory or repository root
            resolved_path = Path.cwd() / resolved_path

        if not resolved_path.exists():
            raise FileNotFoundError(
                f"FastAI classifier checkpoint not found at: {resolved_path}"
            )

        self.model_path = resolved_path
        self.model_version = model_version or DEFAULT_MODEL_VERSION
        self.confidence_threshold = confidence_threshold

        logger.info("Loading FastAI waste classifier learner from %s ...", self.model_path)
        self.learn = load_learner(self.model_path)
        self.vocab = list(self.learn.dls.vocab)
        logger.info("FastAI classifier initialized with vocab: %s", self.vocab)

    def _load_image(self, sanitized_input: str) -> Image.Image:
        """Decode and open image from Data URI, HTTP URL, or local file path."""
        # 1. Base64 Data URI
        if sanitized_input.startswith("data:"):
            try:
                _, b64_part = sanitized_input.split(",", 1)
                img_bytes = base64.b64decode(b64_part)
                return Image.open(io.BytesIO(img_bytes)).convert("RGB")
            except Exception as exc:
                raise ImageValidationError(f"Failed to decode Base64 data URI: {exc}") from exc

        # 2. Remote HTTP/HTTPS URL
        if sanitized_input.startswith(("http://", "https://")):
            try:
                req = Request(
                    sanitized_input,
                    headers={"User-Agent": "EcoSense-AI-Classifier/2.0"},
                )
                with urlopen(req, timeout=10) as resp:
                    data = resp.read()
                return Image.open(io.BytesIO(data)).convert("RGB")
            except Exception as exc:
                raise ImageValidationError(f"Failed to fetch image from URL: {exc}") from exc

        # 3. Local file reference
        file_path = Path(sanitized_input)
        if not file_path.is_absolute():
            file_path = Path.cwd() / file_path

        if not file_path.exists():
            raise ImageValidationError(f"Local image file not found: {file_path}")

        try:
            return Image.open(file_path).convert("RGB")
        except Exception as exc:
            raise ImageValidationError(f"Failed to open image file: {exc}") from exc

    def classify(self, image_input: str) -> ClassificationPrediction:
        """Classify a waste item given an image reference or data URI.

        Args:
            image_input: Validated URI, data URI, or local path for the image.

        Returns:
            ClassificationPrediction: Standard prediction containing campus category,
                                      confidence score, model version, and class probabilities.
        """
        sanitized = validate_image_reference(image_input)
        img = self._load_image(sanitized)

        # Run inference through FastAI learner
        pred, pred_idx, probs = self.learn.predict(img)
        raw_pred_str = str(pred).lower().strip()
        confidence = float(probs[pred_idx])

        # Map FastAI prediction to standard EcoSense campus category
        mapped_class = FASTAI_TO_ECOSENSE_CLASS_MAP.get(
            raw_pred_str,
            "DRY_RECYCLABLE",  # Safe default if an unexpected label appears
        )

        all_probs: Dict[str, float] = {
            str(cls_label): round(float(prob_val), 4)
            for cls_label, prob_val in zip(self.vocab, probs)
        }

        return ClassificationPrediction(
            predicted_class=mapped_class,
            confidence_score=round(confidence, 4),
            model_version=self.model_version,
            metadata={
                "raw_prediction": raw_pred_str,
                "probabilities": all_probs,
                "framework": "fastai",
                "model_file": self.model_path.name,
            },
        )

import base64
import io
from pathlib import Path
from PIL import Image
import pytest

from ai.classification.fastai_model import FastAIWasteClassifier, FASTAI_TO_ECOSENSE_CLASS_MAP
from ai.classification.preprocessing import ImageValidationError


@pytest.fixture
def sample_data_uri() -> str:
    """Generate a valid base64 PNG data URI in memory."""
    img = Image.new("RGB", (100, 100), color=(120, 180, 220))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def test_fastai_classifier_initialization():
    """Verify FastAIWasteClassifier loads the real model checkpoint and populates vocabulary."""
    model_path = Path("ai/models/waste_classifier_v2.pkl")
    if not model_path.exists():
        pytest.skip("Model checkpoint waste_classifier_v2.pkl not found.")

    classifier = FastAIWasteClassifier(
        model_path=model_path,
        model_version="v2.0-fastai",
    )
    assert classifier.learn is not None
    assert len(classifier.vocab) > 0
    # Expected fastai vocab
    assert "cardboard" in classifier.vocab
    assert "plastic" in classifier.vocab
    assert "organic" in classifier.vocab


def test_fastai_classifier_inference_on_data_uri(sample_data_uri: str):
    """Verify inference pipeline processes a Data URI and returns valid campus category."""
    model_path = Path("ai/models/waste_classifier_v2.pkl")
    if not model_path.exists():
        pytest.skip("Model checkpoint waste_classifier_v2.pkl not found.")

    classifier = FastAIWasteClassifier(
        model_path=model_path,
        model_version="v2.0-fastai",
    )
    prediction = classifier.classify(sample_data_uri)

    assert prediction.model_version == "v2.0-fastai"
    assert 0.0 <= prediction.confidence_score <= 1.0
    assert prediction.predicted_class in {
        "WET_ORGANIC",
        "DRY_RECYCLABLE",
        "PAPER",
        "METAL",
        "E_WASTE",
        "GARDEN",
    }
    assert "raw_prediction" in prediction.metadata
    assert prediction.metadata["framework"] == "fastai"
    assert len(prediction.metadata["probabilities"]) == len(classifier.vocab)


def test_fastai_classifier_invalid_image():
    """Verify classifier raises ImageValidationError when given malformed data."""
    model_path = Path("ai/models/waste_classifier_v2.pkl")
    if not model_path.exists():
        pytest.skip("Model checkpoint waste_classifier_v2.pkl not found.")

    classifier = FastAIWasteClassifier(model_path=model_path)
    with pytest.raises(ImageValidationError):
        classifier.classify("data:image/png;base64,not_valid_base64_data!!!")


def test_fastai_class_mapping_completeness():
    """Verify every class in the model vocabulary is mapped to an EcoSense campus waste type."""
    model_path = Path("ai/models/waste_classifier_v2.pkl")
    if not model_path.exists():
        pytest.skip("Model checkpoint waste_classifier_v2.pkl not found.")

    classifier = FastAIWasteClassifier(model_path=model_path)
    for vocab_item in classifier.vocab:
        mapped = FASTAI_TO_ECOSENSE_CLASS_MAP.get(vocab_item)
        assert mapped is not None, f"Vocab item '{vocab_item}' has no mapping in FASTAI_TO_ECOSENSE_CLASS_MAP"
        assert mapped in {
            "WET_ORGANIC",
            "DRY_RECYCLABLE",
            "PAPER",
            "METAL",
            "E_WASTE",
            "GARDEN",
        }

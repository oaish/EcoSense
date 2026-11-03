"""Quick CLI tool to test waste images against the EcoSense AI Classifier.

Usage:
    python test_classifier.py path/to/waste_image.jpg
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ai.classification.fastai_model import FastAIWasteClassifier

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_classifier.py <path_or_url_to_image>")
        print("Example: python test_classifier.py sample.jpg")
        return

    image_input = sys.argv[1]
    print(f"Loading FastAI Waste Classifier...")
    classifier = FastAIWasteClassifier(
        model_path="ai/models/waste_classifier_v2.pkl",
        model_version="v2.0-fastai",
    )

    print(f"\nAnalyzing image: {image_input} ...")
    prediction = classifier.classify(image_input)

    print("\n" + "=" * 50)
    print(f"  PREDICTED CAMPUS BIN : {prediction.predicted_class}")
    print(f"  CONFIDENCE SCORE     : {prediction.confidence_score * 100:.1f}%")
    print(f"  RAW MODEL OUTPUT     : {prediction.metadata.get('raw_prediction')}")
    print(f"  MODEL VERSION        : {prediction.model_version}")
    print("=" * 50)
    print("\nProbability Breakdown:")
    for label, prob in prediction.metadata.get("probabilities", {}).items():
        bar = "#" * int(prob * 30)
        print(f"  {label:12} : {prob * 100:5.1f}%  {bar}")

if __name__ == "__main__":
    main()

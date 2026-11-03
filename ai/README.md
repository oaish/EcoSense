# EcoSense AI/ML Subsystem

This directory contains AI and Machine Learning models, inference abstractions, preprocessing pipelines, and model evaluation modules for the **EcoSense: AI-Based Zero Waste Campus Management Platform** (Don Bosco Institute of Technology, Mumbai).

---

## 1. Directory Structure

```text
ai/
├── README.md                    # Subsystem documentation and architecture guide
├── models/                      # Directory for serialized model checkpoints (.onnx, .pt, etc.)
│   └── .gitkeep
├── classification/              # Computer Vision waste classification module
│   ├── __init__.py              # Module exports
│   ├── classifier.py            # Base abstract classifier interface and prediction dataclass
│   ├── model.py                 # Development/Mock classifier implementation
│   ├── preprocessing.py         # Image reference validation and security sanitization
│   └── config.py                # Subsystem configuration and default parameters
│
└── prediction/                  # Time-Series Waste Accumulation & Fill Prediction module
    ├── __init__.py              # Module exports
    ├── predictor.py             # Base abstract predictor interface and result dataclass
    ├── model.py                 # Baseline fill accumulation rate predictor (baseline-v1)
    ├── features.py              # Time-series feature extraction and collection boundary handler
    ├── preprocessing.py         # Chronological sorting, rate calculations, datetime normalization
    ├── evaluation.py            # Forecasting evaluation metrics (MAE, RMSE, chronological split)
    └── config.py                # Prediction horizons and data thresholds
```

---

## 2. AI Subsystems Architecture

### 2.1 AI Waste Classification (Computer Vision)
- **Input:** Image URL / reference.
- **Output:** Categorized waste class (`WET_ORGANIC`, `DRY_RECYCLABLE`, `PAPER`, `METAL`, `E_WASTE`, `GARDEN`), confidence score, and model version.
- **Status:** Development baseline classifier (`v1.0-mock`) implemented behind [`BaseWasteClassifier`](file:///c:/dev/web/EcoSense/ai/classification/classifier.py).

### 2.2 Waste Generation & Bin Fill Forecasting (Time-Series)
- **Input:** Historical `bin_fill_readings`, `collection_records`, `disposal_records`, and target horizon.
- **Output:** Predicted fill percentage ($0.0\% - 100.0\%$), target timestamp, uncertainty bounds, and model version.
- **Status:** Development baseline rate extrapolation model (`baseline-v1`) implemented behind [`BaseFillPredictor`](file:///c:/dev/web/EcoSense/ai/prediction/predictor.py).

```text
Incoming API Request (POST /api/v1/bins/{id}/predictions)
                     │
                     ▼
        PredictionService (Backend)
  - Fetches historical telemetry for target bin
  - Verifies minimum readings threshold (>= 3)
                     │
                     ▼
  Feature Extractor (ai.prediction.features)
  - Segments readings to current post-collection cycle
  - Calculates accumulation rate (%/hour)
  - Enforces strict no-leakage time boundary
                     │
                     ▼
    BaseFillPredictor (Abstract Interface)
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
BaselineFillPredictor     [Future] XGBoost / LSTM /
(Linear Rate Model)        Transformer Forecaster
         │                       │
         └───────────┬───────────┘
                     ▼
           FillPredictionResult
     (fill %, bounds, timestamps, version)
                     │
                     ▼
   Database Persistence (fill_predictions)
```

---

## 3. Feature Pipeline & Data Handling

1. **Cycle Boundary Segmentation:** Waste collection events reset bin capacity ($85\% \rightarrow 0\%$). The feature pipeline (`segment_cycle_readings`) segments historical telemetry so accumulation rates are computed strictly within the active accumulation cycle.
2. **Irregular Interval Handling:** Readings do not occur at fixed intervals. The rate calculator weights progression across variable durations and handles zero or negative intervals safely.
3. **Strict No-Leakage Temporal Boundary:** Only telemetry recorded at or before `prediction_timestamp` is used during feature extraction.
4. **Data Sufficiency Threshold:** Configurable via `MIN_PREDICTION_READINGS` (default: `3`). Bins with sparse data return HTTP 422 ("Insufficient historical data for prediction").

---

## 4. Forecasting Model Evaluation

Located in [`ai/prediction/evaluation.py`](file:///c:/dev/web/EcoSense/ai/prediction/evaluation.py):
- **Metrics:**
  - **Mean Absolute Error (MAE):** $\text{MAE} = \frac{1}{N} \sum |y_i - \hat{y}_i|$
  - **Root Mean Squared Error (RMSE):** $\text{RMSE} = \sqrt{\frac{1}{N} \sum (y_i - \hat{y}_i)^2}$
- **Chronological Train/Test Split:** Standard random cross-validation is invalid for time-series forecasting. Evaluation uses chronological order (`chronological_train_test_split`) where training data strictly precedes test data.
- **Baseline Comparison Principle:** Any future machine learning model (e.g. XGBoost, LSTM) must be evaluated against the linear baseline (`BaselineFillPredictor`) on real campus datasets before deployment.

---

## 5. Development vs. Production Status

| Subsystem / Component | Status | Description |
| :--- | :--- | :--- |
| **Classifier Interface** | **IMPLEMENTED** | `BaseWasteClassifier` abstract class |
| **Mock Waste Classifier** | **IMPLEMENTED** | Deterministic keyword and hash-based mock (`v1.0-mock`) |
| **Predictor Interface** | **IMPLEMENTED** | `BaseFillPredictor` abstract class |
| **Baseline Predictor** | **IMPLEMENTED** | Linear accumulation rate model (`baseline-v1`) with bounded uncertainty |
| **Feature Extraction** | **IMPLEMENTED** | Post-collection cycle segmentation and rate calculation |
| **Forecast Evaluation** | **IMPLEMENTED** | Time-aware MAE, RMSE, and chronological splitting |
| **Deep Learning Vision Weights** | **IMPLEMENTED** | FastAI / PyTorch vision learner (`waste_classifier_v2.pkl`, `v2.0-fastai`) |
| **Advanced ML Forecasters** | *FUTURE* | XGBoost / LSTM models trained on long-term campus accumulation history |

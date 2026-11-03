# EcoSense AI/ML Implementation Audit Report
**Project:** EcoSense — AI-Based Zero Waste Campus Management Platform  
**Institution:** Don Bosco Institute of Technology (DBIT), Mumbai  
**Audit Date:** September 2026  
**Document Version:** 1.0 (Phase 12 Comprehensive Audit)  
**Status:** FACTUAL ARCHITECTURAL AUDIT (REPORT-ONLY)

---

## 1. Executive Summary

This audit report provides an objective, transparent, and rigorous technical review of all Artificial Intelligence (AI) and Machine Learning (ML) subsystems currently present, architected, or planned in the EcoSense codebase.

The goal of this audit is academic and technical integrity: clearly separating **production software architecture and operational pipelines** from **statistical/machine learning model maturity**. 

### Key Findings
1. **Solid Production Abstraction Layer:** The repository implements enterprise-grade, clean abstract interfaces (`BaseWasteClassifier` in `ai.classification.classifier` and `BaseFillPredictor` in `ai.prediction.predictor`), complete feature extraction pipelines, mathematical evaluation utilities, schema validations, and database persistence layers.
2. **Current Model Status:**
   - **Computer Vision Waste Classification:** Currently operates using a **deterministic keyword and SHA-256 hash-based development mock** (`MockWasteClassifier`, version `v1.0-mock`). **No deep learning model weights** (e.g. PyTorch `.pt`, TensorFlow `.h5`, or ONNX `.onnx`) are currently loaded or trained.
   - **Waste Generation / Bin Fill Forecasting:** Currently operates using an **algorithmic linear accumulation rate baseline model** (`BaselineFillPredictor`, version `baseline-v1`). It performs time-series cycle segmentation, rate calculation (%/hour), bounded uncertainty forecasting, and physical clamping, but is a **deterministic heuristic/statistical baseline rather than a trained neural network/gradient-boosted regressor**.
3. **Operational Readiness:** Both modules are fully connected to the FastAPI backend API endpoints, verified by automated unit and integration test suites, and integrated into responsive frontend UI workflows with camera capture and drag-and-drop file upload.

---

## 2. AI/ML Module Inventory

| Module Name | Purpose | Location in Repository | Input Format | Output Format | Algorithm / Model | Training Status | Inference Status | Persistence | API Integration | Frontend Integration | Testing Status | Implementation Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Waste Classifier Abstraction** | Abstract contract for vision classification | `ai/classification/classifier.py` | String URL / binary reference | `ClassificationPrediction` dataclass | Python ABC (`BaseWasteClassifier`) | N/A | N/A | None | N/A | N/A | Unit tested | **IMPLEMENTED** |
| **Mock Waste Classifier** | Offline deterministic material prediction | `ai/classification/model.py` | Sanitized image reference / keyword | Class name, confidence (0.0–1.0), version | Keyword matching + SHA-256 deterministic fallback | NOT TRAINED (Rule-based) | Active (CPU) | `waste_classifications` table | `POST /api/v1/classification` & `POST /api/v1/classification/upload` | `AIClassificationPage.tsx` | 21 backend tests passing | **MOCK / BASELINE** |
| **Image Preprocessor** | File validation, MIME check & URI sanitization | `ai/classification/preprocessing.py` | Raw file stream / string URL | Sanitized reference string | Security regex & MIME signature inspection | N/A | Active (CPU) | Temp files / Object storage | Integrated in API endpoints | Integrated in Upload/Camera flow | Tested | **IMPLEMENTED** |
| **Fill Predictor Abstraction** | Abstract contract for time-series fill forecasting | `ai/prediction/predictor.py` | `BinFillFeatures` dataclass, timestamps | `FillPredictionResult` dataclass | Python ABC (`BaseFillPredictor`) | N/A | N/A | None | N/A | N/A | Unit tested | **IMPLEMENTED** |
| **Baseline Fill Predictor** | Linear fill rate extrapolation with uncertainty | `ai/prediction/model.py` | `BinFillFeatures` (rate, current fill, horizon) | Predicted fill %, confidence, lower/upper bounds | Rate-based extrapolation: $\hat{y} = \text{clamp}(y_0 + r \cdot \Delta t, 0, 100)$ | NOT TRAINED (Heuristic/Statistical) | Active (CPU) | `fill_predictions` table | `POST /api/v1/bins/{id}/predictions` | `CollectorPredictionsPage.tsx` | 16 backend tests passing | **BASELINE / PROTOTYPE** |
| **Time-Series Feature Extractor** | Cycle segmentation, rate computation & temporal encoding | `ai/prediction/features.py` & `preprocessing.py` | Chronological readings, collection logs, disposals | `BinFillFeatures` | Cycle boundary segmentation & weighted rate calculation | N/A | Active (CPU) | Ephemeral vector | Integrated in `prediction_service` | Visualized in Admin/Collector dashboards | Thoroughly tested | **IMPLEMENTED** |
| **Forecast Evaluator** | Mathematical forecasting evaluation metrics | `ai/prediction/evaluation.py` | Sequences $y_{\text{true}}, y_{\text{pred}}$ | MAE, RMSE, chronological partitions | MAE, RMSE, Chronological Split | N/A | Standalone utility | None | Internal service utility | None | Unit tested | **IMPLEMENTED** |
| **Deep Learning Vision Classifier** | Pretrained CNN/ViT on DBIT waste categories | `ai/models/` | RGB Image Tensor $(3 \times 224 \times 224)$ | Probability distribution over 6 waste classes | MobileNetV3 / EfficientNet / YOLO-v8 | **NOT IMPLEMENTED** | Inactive | `ai/models/` (.onnx/.pt) | Ready for drop-in replacement | Ready for drop-in replacement | Pipeline tests ready | **PLANNED** |
| **Advanced Fill Forecaster** | Supervised multi-step regression | `ai/models/` | Temporal feature matrix | Multi-step forecast vector | XGBoost / LightGBM / LSTM | **NOT IMPLEMENTED** | Inactive | `ai/models/` (.joblib/.pt) | Ready for drop-in replacement | Ready for drop-in replacement | Benchmark harness ready | **PLANNED** |

---

## 3. Waste Classification Subsystem

### 3.1 Architecture & Abstraction
The classification subsystem is architected in [`ai/classification/`](file:///c:/dev/web/EcoSense/ai/classification/):
- **Base Interface:** `BaseWasteClassifier` defines the abstract method `classify(image_input: str) -> ClassificationPrediction`.
- **Data Transfer Object:** `ClassificationPrediction` encapsulates `predicted_class`, `confidence_score`, `model_version`, and extensible `metadata` dictionary.
- **Config:** `default_classifier_config` defines supported classes: `WET_ORGANIC`, `DRY_RECYCLABLE`, `PAPER`, `METAL`, `E_WASTE`, `GARDEN`.

### 3.2 Current Implementation Reality
- **Nature:** The current implementation `MockWasteClassifier` in [`ai/classification/model.py`](file:///c:/dev/web/EcoSense/ai/classification/model.py) is a **deterministic rule and cryptographic hash-based mock**.
- **Keyword Rules:** Keywords such as `"bottle"`, `"plastic"`, `"can"` map to `DRY_RECYCLABLE`; `"banana"`, `"food"`, `"organic"` map to `WET_ORGANIC`; `"battery"`, `"cable"`, `"phone"` map to `E_WASTE`.
- **Fallback Behavior:** For non-matching strings or arbitrary URLs, a SHA-256 hash of the input string is calculated to deterministically select a category and generate a confidence score between $0.75$ and $0.98$.
- **Real ML Vision Model:** **NO**. There is currently no active convolutional neural network (CNN), Vision Transformer (ViT), or neural network inference runtime (e.g. PyTorch, ONNX Runtime, TensorFlow) executing computer vision tensor transformations.
- **Confidence & Low-Confidence State:** Confidence threshold is configured at $0.70$ (`0.70` by default). When confidence falls below this threshold or test inputs contain keywords like `"blurry"`, `"uncertain"`, the system returns `low_confidence = True`, and the frontend displays a dedicated warning banner advising physical bin inspection.
- **Backend Persistence:** Every inference is persisted immutably in the PostgreSQL `waste_classifications` table with timestamp, user ID, image URL, predicted waste type ID, confidence score, and model version.
- **Safety Architecture:** AI classification **never** automatically logs a waste disposal or awards gamification points. The user must proceed to scan the physical QR code on the campus bin to record disposal.

---

## 4. Fill Prediction Subsystem

### 4.1 Architecture & Abstraction
The time-series forecasting subsystem is architected in [`ai/prediction/`](file:///c:/dev/web/EcoSense/ai/prediction/):
- **Base Interface:** `BaseFillPredictor` defines `predict(features: BinFillFeatures, prediction_timestamp: datetime, target_timestamp: datetime) -> FillPredictionResult`.
- **Feature Vector:** `BinFillFeatures` contains 13 engineered features, including `current_fill_percentage`, `fill_rate_per_hour`, `time_since_last_reading_hours`, `time_since_last_collection_hours`, `last_collection_fill_after`, `disposal_events_count`, `hour_of_day`, `day_of_week`, `horizon_hours`, `waste_type_name`, and `capacity_litres`.

### 4.2 Current Implementation Reality
- **Nature:** The current model `BaselineFillPredictor` in [`ai/prediction/model.py`](file:///c:/dev/web/EcoSense/ai/prediction/model.py) is a **deterministic accumulation rate extrapolation baseline** (`baseline-v1`).
- **Mathematical Formula:**
  $$\hat{y} = \min\left(100.0, \max\left(0.0, y_{\text{current}} + r_{\text{hourly}} \times \Delta t_{\text{hours}}\right)\right)$$
- **Cycle Segmentation:** Because waste bins undergo abrupt level drops when emptied by collectors ($85\% \rightarrow 0\%$), [`segment_cycle_readings`](file:///c:/dev/web/EcoSense/ai/prediction/preprocessing.py) segments telemetry to isolate the current accumulation cycle, calculating rate $r_{\text{hourly}}$ exclusively on post-collection telemetry.
- **Real ML Time-Series Model:** **NO**. There is currently no trained regression tree (XGBoost/LightGBM), autoregressive statistical model (ARIMA/SARIMAX), or recurrent neural network (LSTM/GRU/Temporal Fusion Transformer).
- **Uncertainty Bounds:** Margin is computed based on data density ($\pm 5.0\%$ if $\ge 5$ readings; $\pm 8.0\%$ otherwise).

---

## 5. AI Preprocessing Pipelines

### 5.1 Image Preprocessing (`ai/classification/preprocessing.py`)
- **Sanitization:** Validates URL structure, removes dangerous shell characters, blocks local file paths (`file://`), and prevents path traversal.
- **Binary Upload Validation:** Validates incoming file content against accepted MIME types (`image/jpeg`, `image/png`, `image/webp`) and enforces a 10MB file size ceiling.
- **Computer Vision Tensor Pipeline Status:** Standard image tensor normalization (e.g., resizing to $224 \times 224 \times 3$, normalization by ImageNet mean $[0.485, 0.456, 0.406]$ and std $[0.229, 0.224, 0.225]$) is **not yet implemented** because deep learning vision weights are not loaded.

### 5.2 Time-Series Preprocessing (`ai/prediction/preprocessing.py`)
- **Chronological Sorting:** Ensures telemetry timestamps are strictly ordered.
- **Datetime Normalization:** Strips timezone discrepancies into UTC-normalized timestamps.
- **Cycle Boundary Isolation:** Automatically identifies collection reset points.
- **Rate Calculation:** Computes weighted change in fill level per elapsed hour ($\Delta \text{fill} / \Delta t$).

---

## 6. Model Evaluation Framework

Located in [`ai/prediction/evaluation.py`](file:///c:/dev/web/EcoSense/ai/prediction/evaluation.py):
1. **Mean Absolute Error (MAE):**
   $$\text{MAE} = \frac{1}{N} \sum_{i=1}^N |y_i - \hat{y}_i|$$
2. **Root Mean Squared Error (RMSE):**
   $$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N (y_i - \hat{y}_i)^2}$$
3. **Chronological Splitting:** Implements `chronological_train_test_split(series, test_ratio=0.2)` to strictly prevent temporal lookahead leakage during evaluation.

### Ground-Truth Availability
- Currently, **no static ground-truth benchmark dataset** is bundled in the repository. Evaluation functions operate on dynamic simulated or operational telemetry collected in the database.
- Formal evaluation metrics (e.g. reported MAE = 4.2%) cannot be claimed until a labeled DBIT campus benchmark dataset is gathered.

---

## 7. Training Pipeline Audit

| Pipeline Stage | Status | Description |
| :--- | :--- | :--- |
| **Dataset Ingestion** | **NOT IMPLEMENTED** | No automated data pipeline pulling photos or IoT telemetry from campus |
| **Dataset Cleaning & Validation** | **PARTIALLY IMPLEMENTED** | Sanitizers and validators exist for inference; offline dataset cleaning scripts do not |
| **Labeling Tool / Interface** | **NOT IMPLEMENTED** | No administrative annotation tool for ground-truth tagging |
| **Train / Validation / Test Splitting** | **IMPLEMENTED** | `chronological_train_test_split` available for time-series data |
| **Offline Training Script** | **NOT IMPLEMENTED** | No `train_vision.py` or `train_predictor.py` scripts present |
| **Hyperparameter Tuning** | **NOT IMPLEMENTED** | No Optuna, Ray Tune, or grid-search pipelines |
| **Model Serialization / Artifact Storage** | **PARTIALLY IMPLEMENTED** | `ai/models/` directory created with `.gitkeep`; serialized weights absent |
| **Model Registry & Versioning** | **PARTIALLY IMPLEMENTED** | Model version strings tracked in database schema (`model_version`); no MLflow/Weights & Biases integration |
| **Deployment / Serving Runtime** | **IMPLEMENTED** | FastAPI endpoints and abstract interfaces ready for runtime weights loading |

---

## 8. Productionization Gap & Technical Requirements

To upgrade the existing software architecture into production-grade trained AI/ML models, the following steps are required:

### 8.1 Computer Vision Waste Classifier
1. **Required Dataset:** 3,000–5,000 photos of waste items captured across DBIT campus environments (canteen food waste, lab electronic components, classroom paper/packaging, beverage bottles, garden leaves).
2. **Required Labels:** 6 discrete classes matching DBIT bins (`WET_ORGANIC`, `DRY_RECYCLABLE`, `PAPER`, `METAL`, `E_WASTE`, `GARDEN`).
3. **Recommended Model Architecture:** MobileNetV3-Small or EfficientNet-B0 fine-tuned with transfer learning, exported to **ONNX format** for fast CPU inference.
4. **Target Metrics:** Multi-class Classification Accuracy $\ge 90\%$, Macro F1-score $\ge 0.88$, Inference Latency $< 150\text{ms}$ on CPU.
5. **Backend Integration:** Replace `MockWasteClassifier` with an `ONNXRuntimeWasteClassifier` implementing `BaseWasteClassifier`.

### 8.2 Waste Fill Forecaster
1. **Required Dataset:** 6–12 months of high-resolution bin fill telemetry ($\ge 10,000$ readings) from diverse DBIT locations across academic semesters, exam periods, and festivals.
2. **Recommended Model Architecture:** Gradient Boosted Trees (LightGBM / XGBoost Regressor) trained on lag features, rolling statistics, day-of-week, and campus academic calendar events.
3. **Target Metrics:** MAE $\le 6.0\%$ fill level on 4-hour horizon, outperforming `BaselineFillPredictor` by at least $25\%$.
4. **Backend Integration:** Replace `BaselineFillPredictor` with `XGBoostFillPredictor` implementing `BaseFillPredictor`.

---

## 9. Recommended Future AI/ML Roadmap

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                       RECOMMENDED 8-STAGE AI/ML ROADMAP                    │
└────────────────────────────────────────────────────────────────────────────┘

  Stage 1: Campus Data Collection
  ├── Capture 2,000+ waste photos under DBIT lighting conditions
  └── Log continuous bin telemetry during regular college terms

  Stage 2: Dataset Curation & Labeling
  ├── Annotate imagery with 6 DBIT standard waste categories
  └── Clean telemetry and label collection boundary anomalies

  Stage 3: Baseline Benchmarking (CURRENT PHASE)
  ├── Mock classifier (v1.0-mock) validated via API
  └── Linear rate predictor (baseline-v1) validated via API

  Stage 4: Supervised Model Training
  ├── Fine-tune MobileNetV3 / EfficientNet on DBIT imagery
  └── Train LightGBM / XGBoost Regressor on time-series telemetry

  Stage 5: Offline Evaluation & Validation
  ├── Measure Top-1 Accuracy, Precision, Recall, and Confusion Matrix
  └── Benchmark MAE/RMSE against baseline-v1 using chronological split

  Stage 6: Serialization & Backend Integration
  ├── Export models to ONNX / TorchScript in ai/models/
  └── Plug ONNX Runtime into BaseWasteClassifier and BaseFillPredictor

  Stage 7: Production Frontend Testing
  ├── Real-world validation with student camera uploads
  └── Verification of real-time inference latency and low-confidence triggers

  Stage 8: Continuous Monitoring & Drift Retraining
  ├── Monitor confidence distributions in waste_classifications
  └── Periodic quarterly retraining on newly verified campus disposals
```

---

## 10. AI/ML Claims & Presentation Integrity Audit

For academic reports, project evaluations, and DBIT institutional presentations, the following terminology adjustments must be maintained:

| Location | Original Phrasing | Recommended Academic Presentation Phrasing | Rationale |
| :--- | :--- | :--- | :--- |
| **System Overview** | "Deep Neural Network waste classification" | "AI Waste Classifier architecture with baseline mock for software evaluation" | No CNN weights are currently loaded; architecture is complete |
| **Fill Prediction** | "Advanced Predictive ML Fill Forecaster" | "Time-Series Fill Forecasting subsystem with Linear Accumulation Rate Baseline" | Distinguishes mathematical rate model from trained deep neural networks |
| **Accuracy Claims** | "95% AI accuracy" | "Confidence scoring threshold (simulated in baseline mock, target 90%+ in future ML model)" | Prevents claiming unverified empirical benchmark numbers |
| **Route Optimization** | "AI-driven vehicle routing" | *Removed from scope* | Removed to maintain focus on zero-waste sorting and campus gamification |
| **Green Index** | "Automated Green Index calculations" | *Designated as future enhancement* | Explicitly kept out of scope to avoid unvalidated composite formulas |

---

## 11. Final AI/ML Status Summary Table

| Module | Current Implementation | Status | Real Trained Model? | What Remains for Production |
| :--- | :--- | :--- | :--- | :--- |
| **Vision Waste Classifier** | `MockWasteClassifier` (`v1.0-mock`) | **MOCK / BASELINE** | ❌ **No** (Rule & hash-based mock) | Real DBIT photo dataset, transfer learning training, ONNX model weights |
| **Bin Fill Forecaster** | `BaselineFillPredictor` (`baseline-v1`) | **BASELINE / PROTOTYPE** | ❌ **No** (Linear rate accumulation model) | Multi-month historical telemetry dataset, LightGBM/XGBoost training, serialized model |
| **Classifier Interface** | `BaseWasteClassifier` | **IMPLEMENTED** | N/A (Software abstraction) | None — ready for drop-in trained model |
| **Predictor Interface** | `BaseFillPredictor` | **IMPLEMENTED** | N/A (Software abstraction) | None — ready for drop-in trained model |
| **Time-Series Features** | `extract_bin_features` | **IMPLEMENTED** | N/A (Data pipeline) | Additional domain features (e.g. rain/campus events) |
| **Model Evaluation** | `ai.prediction.evaluation` | **IMPLEMENTED** | N/A (Mathematical metrics) | Ground-truth campus test dataset |
| **API Endpoints** | FastAPI Classification & Prediction Routes | **IMPLEMENTED** | N/A (Backend service) | None — fully operational |
| **UI Interfaces** | Upload, Camera Capture, Predictor View | **IMPLEMENTED** | N/A (Frontend interface) | None — fully operational |

---

*Report prepared by Antigravity AI Engineering Team for the Don Bosco Institute of Technology (DBIT) EcoSense Project.*

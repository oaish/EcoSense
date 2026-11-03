import math
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from ai.prediction.evaluation import (
    calculate_mae,
    calculate_rmse,
    chronological_train_test_split,
    evaluate_forecast_metrics,
)
from ai.prediction.features import BinFillFeatures, extract_bin_features
from ai.prediction.model import BaselineFillPredictor
from ai.prediction.preprocessing import calculate_fill_rate_per_hour, segment_cycle_readings
from ai.prediction.predictor import BaseFillPredictor, FillPredictionResult
from app.models.bin import Bin
from app.models.collection import CollectionRecord
from app.models.disposal import DisposalRecord
from ai.prediction.config import default_prediction_config
from app.models.fill_reading import BinFillReading
from app.models.location import Location
from app.models.prediction import FillPrediction
from app.models.user import User
from app.models.waste_type import WasteType
from app.services.prediction_service import set_predictor


# ---------------------------------------------------------------------------
# API & Access Control Tests
# ---------------------------------------------------------------------------


def test_collector_and_admin_can_generate_prediction(
    client: TestClient,
    collector_token: str,
    admin_token: str,
    test_bin: Bin,
    db_session: Session,
):
    """Test 1 & 2: Collector and Admin roles can trigger prediction generation."""
    # Seed 5 historical readings spaced 1 hour apart
    now = datetime.now(timezone.utc)
    for i, fill in enumerate([10.0, 20.0, 32.0, 45.0, 58.0]):
        r = BinFillReading(
            bin_id=test_bin.bin_id,
            fill_percentage=Decimal(str(fill)),
            recorded_at=now - timedelta(hours=5 - i),
            source="MANUAL",
        )
        db_session.add(r)
    db_session.commit()

    # 1. Collector triggers prediction
    res_collector = client.post(
        f"/api/v1/bins/{test_bin.bin_id}/predictions",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"horizon_minutes": 120},
    )
    assert res_collector.status_code == 201
    data_c = res_collector.json()
    assert "prediction_id" in data_c
    assert data_c["bin_id"] == str(test_bin.bin_id)
    assert data_c["model_version"] == "baseline-v1"
    assert data_c["predicted_fill_percentage"] > 58.0
    assert 0.0 <= data_c["predicted_fill_percentage"] <= 100.0

    # 2. Admin triggers prediction
    res_admin = client.post(
        f"/api/v1/bins/{test_bin.bin_id}/predictions",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_admin.status_code == 201
    data_a = res_admin.json()
    assert data_a["prediction_id"] != data_c["prediction_id"]


def test_student_and_staff_cannot_generate_prediction(
    client: TestClient,
    student_token: str,
    staff_token: str,
    test_bin: Bin,
):
    """Test 3 & 4: Students and Staff are rejected from triggering predictions (403 Forbidden)."""
    res_student = client.post(
        f"/api/v1/bins/{test_bin.bin_id}/predictions",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res_student.status_code == 403

    res_staff = client.post(
        f"/api/v1/bins/{test_bin.bin_id}/predictions",
        headers={"Authorization": f"Bearer {staff_token}"},
    )
    assert res_staff.status_code == 403


def test_unauthenticated_request_rejected(client: TestClient, test_bin: Bin):
    """Test 5: Unauthenticated request is rejected with 401."""
    res = client.post(f"/api/v1/bins/{test_bin.bin_id}/predictions")
    assert res.status_code == 401


def test_nonexistent_bin_returns_404(client: TestClient, admin_token: str):
    """Test 6: Requesting prediction for nonexistent bin returns 404."""
    fake_id = uuid.uuid4()
    res = client.post(
        f"/api/v1/bins/{fake_id}/predictions",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 404
    assert "Bin not found" in res.json()["detail"]


def test_insufficient_historical_data_returns_422(
    client: TestClient,
    admin_token: str,
    test_location: Location,
    test_waste_type: WasteType,
    db_session: Session,
):
    """Test 7: Bins with fewer than MIN_PREDICTION_READINGS return 422 with a helpful error."""
    sparse_bin = Bin(
        bin_code="SPARSE-BIN-01",
        location_id=test_location.location_id,
        waste_type_id=test_waste_type.waste_type_id,
        capacity_litres=Decimal("60.00"),
        current_fill_percentage=Decimal("10.00"),
        status="ACTIVE",
    )
    db_session.add(sparse_bin)
    db_session.commit()
    db_session.refresh(sparse_bin)

    # Only 1 reading exists (less than minimum 3)
    r1 = BinFillReading(
        bin_id=sparse_bin.bin_id,
        fill_percentage=Decimal("10.00"),
        recorded_at=datetime.now(timezone.utc) - timedelta(hours=1),
        source="MANUAL",
    )
    db_session.add(r1)
    db_session.commit()

    res = client.post(
        f"/api/v1/bins/{sparse_bin.bin_id}/predictions",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 422
    assert "Insufficient historical data for prediction" in res.json()["detail"]


def test_prediction_output_properties_and_persistence(
    client: TestClient,
    admin_token: str,
    test_bin: Bin,
    db_session: Session,
):
    """Test 8, 9, 10, 11, 12, 13: Prediction values, bounds, timestamps, and DB persistence."""
    now = datetime.now(timezone.utc)
    for i, fill in enumerate([20.0, 35.0, 50.0]):
        r = BinFillReading(
            bin_id=test_bin.bin_id,
            fill_percentage=Decimal(str(fill)),
            recorded_at=now - timedelta(hours=3 - i),
            source="MANUAL",
        )
        db_session.add(r)
    db_session.commit()

    res = client.post(
        f"/api/v1/bins/{test_bin.bin_id}/predictions",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"horizon_minutes": 60},
    )
    assert res.status_code == 201
    body = res.json()

    # 1. Bounded fill percentage
    assert 0.0 <= body["predicted_fill_percentage"] <= 100.0
    # 2. Timestamps verification: prediction_timestamp < target_timestamp
    pred_t = datetime.fromisoformat(body["prediction_timestamp"])
    target_t = datetime.fromisoformat(body["target_timestamp"])
    assert target_t > pred_t
    # 3. Model version
    assert body["model_version"] == "baseline-v1"
    # 4. Uncertainty bounds
    assert body["lower_bound"] <= body["predicted_fill_percentage"] <= body["upper_bound"]

    # 5. Verify in DB
    db_rec = (
        db_session.query(FillPrediction)
        .filter(FillPrediction.prediction_id == body["prediction_id"])
        .first()
    )
    assert db_rec is not None
    assert db_rec.bin_id == test_bin.bin_id


def test_prediction_history_retrieval_and_pagination(
    client: TestClient,
    admin_token: str,
    student_token: str,
    test_bin: Bin,
    db_session: Session,
):
    """Test 14 & 15: Prediction history can be retrieved and paginated by authenticated users."""
    # Seed 4 predictions for test_bin
    now = datetime.now(timezone.utc)
    for i in range(4):
        pred = FillPrediction(
            bin_id=test_bin.bin_id,
            predicted_fill_percentage=Decimal("65.50"),
            prediction_timestamp=now - timedelta(minutes=10 * i),
            target_timestamp=now + timedelta(hours=2),
            model_version="baseline-v1",
        )
        db_session.add(pred)
    db_session.commit()

    # List with pagination
    res = client.get(
        f"/api/v1/bins/{test_bin.bin_id}/predictions?skip=0&limit=2",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 2

    # Get single prediction by ID
    pred_id = items[0]["prediction_id"]
    res_single = client.get(
        f"/api/v1/predictions/{pred_id}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res_single.status_code == 200
    assert res_single.json()["prediction_id"] == pred_id


def test_historical_tables_remain_unmodified(
    client: TestClient,
    admin_token: str,
    test_bin: Bin,
    test_student_user: User,
    test_collector_user: User,
    db_session: Session,
):
    """Test 17, 18, 19: Predictions do NOT modify historical fill readings, collections, or disposals."""
    now = datetime.now(timezone.utc)

    # 1. Historical readings
    for fill in [10.0, 25.0, 40.0]:
        db_session.add(
            BinFillReading(
                bin_id=test_bin.bin_id,
                fill_percentage=Decimal(str(fill)),
                recorded_at=now - timedelta(hours=4),
                source="MANUAL",
            )
        )

    # 2. Historical collection
    coll = CollectionRecord(
        bin_id=test_bin.bin_id,
        collector_id=test_collector_user.user_id,
        fill_level_before=Decimal("80.00"),
        collected_quantity_kg=Decimal("15.00"),
        fill_level_after=Decimal("0.00"),
        collected_at=now - timedelta(hours=5),
    )
    db_session.add(coll)

    # 3. Disposal record
    disp = DisposalRecord(
        bin_id=test_bin.bin_id,
        user_id=test_student_user.user_id,
        quantity_kg=Decimal("1.20"),
        recorded_at=now - timedelta(hours=3),
    )
    db_session.add(disp)
    db_session.commit()

    readings_count_before = db_session.query(BinFillReading).count()
    collections_count_before = db_session.query(CollectionRecord).count()
    disposals_count_before = db_session.query(DisposalRecord).count()

    # Trigger prediction
    res = client.post(
        f"/api/v1/bins/{test_bin.bin_id}/predictions",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 201

    # Verify counts remain exactly identical
    assert db_session.query(BinFillReading).count() == readings_count_before
    assert db_session.query(CollectionRecord).count() == collections_count_before
    assert db_session.query(DisposalRecord).count() == disposals_count_before


def test_predictor_abstraction_and_swap(
    client: TestClient,
    admin_token: str,
    test_bin: Bin,
    db_session: Session,
):
    """Test 20: Predictor abstraction allows swapping model implementation without route changes."""
    now = datetime.now(timezone.utc)
    for fill in [10.0, 20.0, 30.0]:
        db_session.add(
            BinFillReading(
                bin_id=test_bin.bin_id,
                fill_percentage=Decimal(str(fill)),
                recorded_at=now - timedelta(hours=2),
                source="MANUAL",
            )
        )
    db_session.commit()

    class CustomXGBoostPredictor(BaseFillPredictor):
        def predict(
            self,
            features: BinFillFeatures,
            prediction_timestamp: datetime,
            target_timestamp: datetime,
        ) -> FillPredictionResult:
            return FillPredictionResult(
                predicted_fill_percentage=88.88,
                prediction_timestamp=prediction_timestamp,
                target_timestamp=target_timestamp,
                model_version="xgboost-experimental-v2",
                confidence_score=0.95,
                lower_bound=85.0,
                upper_bound=92.0,
                metadata={"algorithm": "gradient_boosted_trees"},
            )

    set_predictor(CustomXGBoostPredictor())
    try:
        res = client.post(
            f"/api/v1/bins/{test_bin.bin_id}/predictions",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["predicted_fill_percentage"] == 88.88
        assert data["model_version"] == "xgboost-experimental-v2"
        assert data["confidence_score"] == 0.95
    finally:
        set_predictor(None)


# ---------------------------------------------------------------------------
# Feature Engineering & Time-Series Unit Tests
# ---------------------------------------------------------------------------


def test_feature_extraction_chronology_and_fill_rate():
    """Test 21a: Chronological readings correctly yield fill rate and handle irregular intervals."""
    t0 = datetime(2026, 9, 18, 8, 0, tzinfo=timezone.utc)
    # Readings at 8:00 (10%), 10:00 (30%), 11:30 (45%) -> Rate is (45-10)/3.5h = 10%/hr
    readings = [
        (t0, 10.0),
        (t0 + timedelta(hours=2), 30.0),
        (t0 + timedelta(hours=3, minutes=30), 45.0),
    ]

    rate = calculate_fill_rate_per_hour(readings)
    assert math.isclose(rate, 10.0, rel_tol=1e-2)

    # Test extraction
    features = extract_bin_features(
        bin_id=uuid.uuid4(),
        prediction_time=t0 + timedelta(hours=4),
        horizon_minutes=120,
        readings=readings,
        collections=[],
        disposals=[],
    )
    assert features.current_fill_percentage == 45.0
    assert math.isclose(features.fill_rate_per_hour, 10.0, rel_tol=1e-2)
    assert features.recent_readings_count == 3
    assert features.horizon_hours == 2.0


def test_feature_extraction_collection_boundary_segmentation():
    """Test 21b: Collection events segment the time-series so old accumulation isn't mixed."""
    t0 = datetime(2026, 9, 18, 8, 0, tzinfo=timezone.utc)
    # Pre-collection: 8:00 (80%), 9:00 (95%)
    # Collection at 10:00 (95% -> 0%)
    # Post-collection: 11:00 (15%), 12:00 (30%) -> Post-collection rate is (30-15)/1h = 15%/hr
    readings = [
        (t0, 80.0),
        (t0 + timedelta(hours=1), 95.0),
        (t0 + timedelta(hours=3), 15.0),
        (t0 + timedelta(hours=4), 30.0),
    ]
    collections = [
        (t0 + timedelta(hours=2), 95.0, 0.0),
    ]

    features = extract_bin_features(
        bin_id=uuid.uuid4(),
        prediction_time=t0 + timedelta(hours=4),
        horizon_minutes=60,
        readings=readings,
        collections=collections,
        disposals=[],
    )
    assert features.current_fill_percentage == 30.0
    assert math.isclose(features.fill_rate_per_hour, 15.0, rel_tol=1e-2)
    assert features.last_collection_fill_after == 0.0
    assert features.time_since_last_collection_hours == 2.0


def test_feature_extraction_no_future_data_leakage():
    """Test 21c: Readings recorded after the prediction timestamp are strictly excluded."""
    t_pred = datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc)
    readings = [
        (t_pred - timedelta(hours=2), 20.0),
        (t_pred - timedelta(hours=1), 35.0),
        (t_pred, 50.0),
        (t_pred + timedelta(hours=1), 99.0),  # FUTURE reading
    ]

    features = extract_bin_features(
        bin_id=uuid.uuid4(),
        prediction_time=t_pred,
        horizon_minutes=60,
        readings=readings,
        collections=[],
        disposals=[],
    )
    assert features.current_fill_percentage == 50.0
    assert features.recent_readings_count == 3


def test_missing_optional_fields_handled_gracefully():
    """Test 21d: Disposals without quantity_kg or collections without fill_level_after don't crash."""
    t_pred = datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc)
    disposals = [
        (t_pred - timedelta(minutes=30), None),  # NULL quantity_kg
    ]
    collections = [
        (t_pred - timedelta(hours=1), None, None),  # NULL before and after
    ]
    readings = [
        (t_pred - timedelta(hours=2), 10.0),
        (t_pred, 20.0),
    ]

    features = extract_bin_features(
        bin_id=uuid.uuid4(),
        prediction_time=t_pred,
        horizon_minutes=60,
        readings=readings,
        collections=collections,
        disposals=disposals,
    )
    assert features.disposal_events_count == 1
    assert features.current_fill_percentage == 20.0


# ---------------------------------------------------------------------------
# Model Evaluation Unit Tests
# ---------------------------------------------------------------------------


def test_evaluation_mae_and_rmse_metrics():
    """Test 22a: MAE and RMSE calculation on deterministic synthetic vectors."""
    y_true = [10.0, 20.0, 30.0, 40.0]
    y_pred = [12.0, 18.0, 33.0, 39.0]
    # Absolute errors: [2, 2, 3, 1] -> Mean = 8/4 = 2.0
    # Squared errors: [4, 4, 9, 1] -> Mean = 18/4 = 4.5 -> RMSE = sqrt(4.5) ≈ 2.1213

    mae = calculate_mae(y_true, y_pred)
    rmse = calculate_rmse(y_true, y_pred)

    assert math.isclose(mae, 2.0, rel_tol=1e-3)
    assert math.isclose(rmse, math.sqrt(4.5), rel_tol=1e-3)

    metrics = evaluate_forecast_metrics(y_true, y_pred)
    assert metrics["mae"] == mae
    assert metrics["rmse"] == rmse
    assert metrics["count"] == 4


def test_chronological_train_test_split():
    """Test 22b: Chronological split maintains strict temporal order."""
    sequence = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    train, test = chronological_train_test_split(sequence, test_ratio=0.3)

    assert len(train) == 7
    assert len(test) == 3
    assert train == [1, 2, 3, 4, 5, 6, 7]
    assert test == [8, 9, 10]
    assert max(train) < min(test)


# ---------------------------------------------------------------------------
# End-to-End Workflow Test
# ---------------------------------------------------------------------------


def test_end_to_end_prediction_scenario(
    client: TestClient,
    admin_token: str,
    collector_token: str,
    test_location: Location,
    test_waste_type: WasteType,
    db_session: Session,
):
    """Test 23 (End-to-End):

    ADMIN creates bin -> Seeds realistic chronological telemetry (10%, 25%, 40%, 55%, 70%) ->
    COLLECTOR requests prediction -> Prediction service extracts features ->
    Baseline predictor forecasts future fill -> Result is stored and retrievable.
    """
    # 1. Admin creates physical bin
    bin_e2e = Bin(
        bin_code="DBIT-PRED-E2E",
        location_id=test_location.location_id,
        waste_type_id=test_waste_type.waste_type_id,
        capacity_litres=Decimal("120.00"),
        current_fill_percentage=Decimal("70.00"),
        status="ACTIVE",
    )
    db_session.add(bin_e2e)
    db_session.commit()
    db_session.refresh(bin_e2e)

    # 2. Seed 5 chronological readings (10% to 70% over 4 hours => ~15%/hr)
    base_t = datetime.now(timezone.utc) - timedelta(hours=4)
    for i, fill in enumerate([10.0, 25.0, 40.0, 55.0, 70.0]):
        db_session.add(
            BinFillReading(
                bin_id=bin_e2e.bin_id,
                fill_percentage=Decimal(str(fill)),
                recorded_at=base_t + timedelta(hours=i),
                source="MANUAL",
            )
        )
    db_session.commit()

    # 3. Collector triggers prediction for 1 hour ahead
    pred_res = client.post(
        f"/api/v1/bins/{bin_e2e.bin_id}/predictions",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"horizon_minutes": 60},
    )
    assert pred_res.status_code == 201
    pred_data = pred_res.json()

    # 4. Verify predicted values: current 70% + ~15%/hr * 1h ≈ 85%
    assert 80.0 <= pred_data["predicted_fill_percentage"] <= 90.0
    assert pred_data["model_version"] == "baseline-v1"
    assert pred_data["target_timestamp"] > pred_data["prediction_timestamp"]

    # 5. Verify prediction appears in historical listing
    history_res = client.get(
        f"/api/v1/bins/{bin_e2e.bin_id}/predictions",
        headers={"Authorization": f"Bearer {collector_token}"},
    )
    assert history_res.status_code == 200
    assert len(history_res.json()) >= 1
    assert history_res.json()[0]["prediction_id"] == pred_data["prediction_id"]

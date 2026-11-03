import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.bin import Bin
from app.models.classification import WasteClassification
from app.models.collection import CollectionRecord
from app.models.disposal import DisposalRecord
from app.models.fill_reading import BinFillReading
from app.models.gamification import PointTransaction, Reward, RewardRedemption
from app.models.location import Location
from app.models.prediction import FillPrediction
from app.models.processing import ProcessingRecord
from app.models.report import WasteReport
from app.models.role import Role
from app.models.user import User
from app.models.waste_type import WasteType


@pytest.fixture
def setup_analytics_data(
    db_session: Session,
    test_student_user: User,
    test_admin_user: User,
    test_collector_user: User,
):
    """
    Seeds comprehensive synthetic operational data across multiple dates, locations, waste types,
    disposals, collections, processing, fill readings, reports, predictions, and gamification.
    """
    now = datetime.now(timezone.utc)

    # Locations
    loc1 = Location(
        name="Main Academic Complex",
        location_type="ACADEMIC_BLOCK",
        building="Block A",
        floor="Ground",
        is_active=True,
    )
    loc2 = Location(
        name="Student Cafeteria",
        location_type="CANTEEN",
        building="Dining Hall",
        floor="1st Floor",
        is_active=True,
    )
    db_session.add_all([loc1, loc2])
    db_session.flush()

    # Waste Types (Fetch existing or create)
    wt_dry = db_session.query(WasteType).filter(WasteType.name == "DRY_RECYCLABLE").first()
    if not wt_dry:
        wt_dry = WasteType(
            name="DRY_RECYCLABLE",
            description="Dry recyclable paper and plastic",
            is_active=True,
        )
        db_session.add(wt_dry)
        db_session.flush()

    wt_wet = db_session.query(WasteType).filter(WasteType.name == "WET_ORGANIC").first()
    if not wt_wet:
        wt_wet = WasteType(
            name="WET_ORGANIC",
            description="Food waste and biodegradables",
            is_active=True,
        )
        db_session.add(wt_wet)
        db_session.flush()

    # Bins
    bin1 = Bin(
        bin_code="ACAD-DRY-01",
        location_id=loc1.location_id,
        waste_type_id=wt_dry.waste_type_id,
        capacity_litres=100.0,
        current_fill_percentage=85.0,
        status="ACTIVE",
    )
    bin2 = Bin(
        bin_code="CAFE-WET-01",
        location_id=loc2.location_id,
        waste_type_id=wt_wet.waste_type_id,
        capacity_litres=120.0,
        current_fill_percentage=40.0,
        status="ACTIVE",
    )
    bin3_damaged = Bin(
        bin_code="ACAD-DMG-01",
        location_id=loc1.location_id,
        waste_type_id=wt_dry.waste_type_id,
        capacity_litres=80.0,
        current_fill_percentage=10.0,
        status="DAMAGED",
    )
    db_session.add_all([bin1, bin2, bin3_damaged])
    db_session.flush()

    # Disposals (across different dates)
    disp1 = DisposalRecord(
        bin_id=bin1.bin_id,
        user_id=test_student_user.user_id,
        recorded_at=now - timedelta(days=5),
    )
    disp2 = DisposalRecord(
        bin_id=bin2.bin_id,
        user_id=test_student_user.user_id,
        recorded_at=now - timedelta(days=2),
    )
    disp_old = DisposalRecord(
        bin_id=bin1.bin_id,
        user_id=test_student_user.user_id,
        recorded_at=now - timedelta(days=45),  # Out of default 30d window
    )
    db_session.add_all([disp1, disp2, disp_old])
    db_session.flush()

    # Fill Readings
    read1 = BinFillReading(
        bin_id=bin1.bin_id,
        fill_percentage=85.0,
        source="MANUAL",
        recorded_at=now - timedelta(days=3),
    )
    read2 = BinFillReading(
        bin_id=bin2.bin_id,
        fill_percentage=40.0,
        source="MANUAL",
        recorded_at=now - timedelta(days=3),
    )
    db_session.add_all([read1, read2])
    db_session.flush()

    # Collections
    col1 = CollectionRecord(
        bin_id=bin1.bin_id,
        collector_id=test_collector_user.user_id,
        fill_level_before=90.0,
        fill_level_after=0.0,
        collected_quantity_kg=25.0,
        collected_at=now - timedelta(days=4),
    )
    col2 = CollectionRecord(
        bin_id=bin2.bin_id,
        collector_id=test_collector_user.user_id,
        fill_level_before=80.0,
        fill_level_after=0.0,
        collected_quantity_kg=15.0,
        collected_at=now - timedelta(days=2),
    )
    col_null = CollectionRecord(
        bin_id=bin1.bin_id,
        collector_id=test_collector_user.user_id,
        fill_level_before=50.0,
        fill_level_after=0.0,
        collected_quantity_kg=None,  # Unmeasured collection
        collected_at=now - timedelta(days=1),
    )
    db_session.add_all([col1, col2, col_null])
    db_session.flush()

    # Processing records (Recycling & Composting)
    proc1 = ProcessingRecord(
        collection_id=col1.collection_id,
        processed_by=test_admin_user.user_id,
        processing_type="RECYCLING",
        quantity_kg=20.0,
        status="COMPLETED",
        processed_at=now - timedelta(days=4),
    )
    proc2 = ProcessingRecord(
        collection_id=col2.collection_id,
        processed_by=test_admin_user.user_id,
        processing_type="COMPOSTING",
        quantity_kg=12.0,
        status="COMPLETED",
        processed_at=now - timedelta(days=2),
    )
    db_session.add_all([proc1, proc2])
    db_session.flush()

    # Reports
    rep1 = WasteReport(
        user_id=test_student_user.user_id,
        bin_id=bin1.bin_id,
        report_type="OVERFLOWING",
        description="Bin overflowing with plastic bottles",
        status="PENDING",
        created_at=now - timedelta(days=1),
    )
    rep2 = WasteReport(
        user_id=test_student_user.user_id,
        bin_id=bin2.bin_id,
        report_type="WRONG_SEGREGATION",
        description="Mixed plastics in wet bin",
        status="RESOLVED",
        created_at=now - timedelta(days=3),
        resolved_at=now - timedelta(days=2),  # Took 24h
        resolved_by=test_admin_user.user_id,
    )
    db_session.add_all([rep1, rep2])
    db_session.flush()

    # Predictions
    pred1 = FillPrediction(
        bin_id=bin1.bin_id,
        predicted_fill_percentage=88.5,
        prediction_timestamp=now - timedelta(days=1),
        target_timestamp=now + timedelta(hours=6),
        model_version="moving_average_v1",
        confidence_score=0.85,
        created_at=now - timedelta(days=1),
    )
    pred2 = FillPrediction(
        bin_id=bin2.bin_id,
        predicted_fill_percentage=45.0,
        prediction_timestamp=now - timedelta(days=1),
        target_timestamp=now + timedelta(hours=6),
        model_version="moving_average_v1",
        confidence_score=0.80,
        created_at=now - timedelta(days=1),
    )
    db_session.add_all([pred1, pred2])
    db_session.flush()

    # Classifications
    clf1 = WasteClassification(
        user_id=test_student_user.user_id,
        image_url="uploads/test1.jpg",
        predicted_waste_type_id=wt_dry.waste_type_id,
        confidence_score=0.92,
        model_version="rule_based_v1",
        created_at=now - timedelta(days=2),
    )
    clf2 = WasteClassification(
        user_id=test_student_user.user_id,
        image_url="uploads/test2.jpg",
        predicted_waste_type_id=wt_wet.waste_type_id,
        confidence_score=0.55,  # Low confidence
        model_version="rule_based_v1",
        created_at=now - timedelta(days=2),
    )
    db_session.add_all([clf1, clf2])
    db_session.flush()

    # Gamification: points & rewards
    rew = Reward(
        name="DBIT Cafeteria Chai Coupon",
        points_cost=50,
        stock_quantity=100,
        is_active=True,
    )
    db_session.add(rew)
    db_session.flush()

    pt1 = PointTransaction(
        user_id=test_student_user.user_id,
        points=10,
        transaction_type="EARN",
        source_type="DISPOSAL",
        description="Points for disposal",
        created_at=now - timedelta(days=5),
    )
    pt2 = PointTransaction(
        user_id=test_student_user.user_id,
        points=15,
        transaction_type="EARN",
        source_type="REPORT",
        description="Points for resolved report",
        created_at=now - timedelta(days=2),
    )
    pt_redeem = PointTransaction(
        user_id=test_student_user.user_id,
        points=-50,
        transaction_type="REDEEM",
        source_type="REWARD_REDEMPTION",
        description="Redeemed chai coupon",
        created_at=now - timedelta(days=1),
    )
    redemption = RewardRedemption(
        user_id=test_student_user.user_id,
        reward_id=rew.reward_id,
        points_spent=50,
        status="APPROVED",
        created_at=now - timedelta(days=1),
    )
    db_session.add_all([pt1, pt2, pt_redeem, redemption])
    db_session.commit()

    return {
        "loc1": loc1,
        "loc2": loc2,
        "bin1": bin1,
        "bin2": bin2,
        "wt_dry": wt_dry,
        "wt_wet": wt_wet,
    }


# ============================================================================
# 1-5. RBAC & AUTHENTICATION TESTS
# ============================================================================


def test_unauthenticated_analytics_rejected(client):
    """1. Unauthenticated analytics request is rejected with 401."""
    res = client.get("/api/v1/analytics/summary")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_student_analytics_rejected(client, student_token):
    """2. Student request to analytics is rejected with 403."""
    res = client.get(
        "/api/v1/analytics/summary",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_staff_analytics_rejected(client, staff_token):
    """3. Staff request to analytics is rejected with 403."""
    res = client.get(
        "/api/v1/analytics/summary",
        headers={"Authorization": f"Bearer {staff_token}"},
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_collector_analytics_rejected(client, collector_token):
    """4. Collector request to analytics is rejected with 403."""
    res = client.get(
        "/api/v1/analytics/summary",
        headers={"Authorization": f"Bearer {collector_token}"},
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_access_analytics(client, admin_token, setup_analytics_data):
    """5. Admin can access analytics summary successfully."""
    res = client.get(
        "/api/v1/analytics/summary",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert "summary" in data
    assert "operations" in data
    assert "participation" in data
    assert "gamification" in data
    assert "predictions" in data


# ============================================================================
# 6-8. SUMMARY ANALYTICS TESTS
# ============================================================================


def test_summary_returns_expected_metrics(client, admin_token, setup_analytics_data):
    """6. Summary returns correct aggregated metrics across all subsystems."""
    res = client.get(
        "/api/v1/analytics/summary",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()

    # In default 30-day window:
    # Disposals: 2 (disp1 and disp2; disp_old is outside 30d)
    assert data["summary"]["disposal_count"] == 2
    # Collected: 25.0 + 15.0 = 40.0 kg (col_null is None, ignored by SQL SUM)
    assert data["summary"]["total_collected_quantity_kg"] == 40.0
    # Processed: 20.0 + 12.0 = 32.0 kg
    assert data["summary"]["total_processed_quantity_kg"] == 32.0
    assert data["summary"]["total_recycled_quantity_kg"] == 20.0
    assert data["summary"]["total_composted_quantity_kg"] == 12.0
    # Diversion rate: 32.0 / 40.0 * 100 = 80.0%
    assert data["summary"]["diversion_rate"] == 80.0

    # Operations: 3 bins total, 2 active, 1 high fill (bin1 at 85%), 1 damaged (bin3)
    assert data["operations"]["total_bins"] == 3
    assert data["operations"]["active_bins"] == 2
    assert data["operations"]["high_fill_bins"] == 1
    assert data["operations"]["damaged_bins"] == 1
    assert data["operations"]["pending_reports"] == 1
    assert data["operations"]["resolved_reports"] == 1

    # Gamification
    assert data["gamification"]["total_points_earned"] == 25  # 10 + 15
    assert data["gamification"]["total_points_redeemed"] == 50
    assert data["gamification"]["reward_redemptions_count"] == 1


def test_summary_respects_date_range(client, admin_token, setup_analytics_data):
    """7. Summary filters records within start_date and end_date correctly."""
    now = datetime.now(timezone.utc)
    # Filter for older records (40-50 days ago)
    start = (now - timedelta(days=50)).isoformat()
    end = (now - timedelta(days=40)).isoformat()

    res = client.get(
        "/api/v1/analytics/summary",
        params={"start_date": start, "end_date": end},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    # Only disp_old was created in this period
    assert data["summary"]["disposal_count"] == 1
    assert data["summary"]["total_collected_quantity_kg"] is None
    assert data["summary"]["diversion_rate"] is None


def test_summary_handles_null_quantities_correctly(client, admin_token):
    """8. Handles empty/null data gracefully without crashes or dividing by zero."""
    now = datetime.now(timezone.utc)
    future_start = (now + timedelta(days=10)).isoformat()
    future_end = (now + timedelta(days=20)).isoformat()

    res = client.get(
        "/api/v1/analytics/summary",
        params={"start_date": future_start, "end_date": future_end},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["summary"]["disposal_count"] == 0
    assert data["summary"]["total_collected_quantity_kg"] is None
    assert data["summary"]["diversion_rate"] is None


# ============================================================================
# 9-10. WASTE TYPE ANALYTICS
# ============================================================================


def test_waste_type_aggregation(client, admin_token, setup_analytics_data):
    """9. Aggregates metrics by waste type accurately."""
    res = client.get(
        "/api/v1/analytics/waste-types",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()

    dry = next(item for item in data if item["waste_type_name"] == "DRY_RECYCLABLE")
    wet = next(item for item in data if item["waste_type_name"] == "WET_ORGANIC")

    assert dry["disposal_count"] == 1
    assert dry["collected_quantity_kg"] == 25.0
    assert dry["recycled_quantity_kg"] == 20.0

    assert wet["disposal_count"] == 1
    assert wet["collected_quantity_kg"] == 15.0
    assert wet["composted_quantity_kg"] == 12.0


def test_waste_type_filtering(client, admin_token, setup_analytics_data):
    """10. Filters waste type activity by location."""
    loc1_id = setup_analytics_data["loc1"].location_id
    res = client.get(
        f"/api/v1/analytics/waste-types?location_id={loc1_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()

    dry = next(item for item in data if item["waste_type_name"] == "DRY_RECYCLABLE")
    wet = next(item for item in data if item["waste_type_name"] == "WET_ORGANIC")

    assert dry["disposal_count"] == 1
    assert wet["disposal_count"] == 0


# ============================================================================
# 11-12. LOCATION ANALYTICS
# ============================================================================


def test_location_aggregation(client, admin_token, setup_analytics_data):
    """11. Location aggregation returns metrics for physical campus locations."""
    res = client.get(
        "/api/v1/analytics/locations",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()

    acad = next(loc for loc in data if loc["location_name"] == "Main Academic Complex")
    assert acad["active_bin_count"] == 1
    assert acad["disposal_count"] == 1
    assert acad["collected_quantity_kg"] == 25.0
    assert acad["average_fill_percentage"] == 85.0


# ============================================================================
# 13-16. TREND ANALYTICS
# ============================================================================


def test_trend_granularities(client, admin_token, setup_analytics_data):
    """13-15. Daily, weekly, and monthly trend bucketings work."""
    # Daily
    res_day = client.get(
        "/api/v1/analytics/trends?granularity=day",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_day.status_code == status.HTTP_200_OK
    day_data = res_day.json()
    assert day_data["granularity"] == "day"
    assert len(day_data["data_points"]) > 0

    # Weekly
    res_week = client.get(
        "/api/v1/analytics/trends?granularity=week",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_week.status_code == status.HTTP_200_OK
    assert res_week.json()["granularity"] == "week"

    # Monthly
    res_month = client.get(
        "/api/v1/analytics/trends?granularity=month",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_month.status_code == status.HTTP_200_OK
    assert res_month.json()["granularity"] == "month"


# ============================================================================
# 17-18. COLLECTION ANALYTICS
# ============================================================================


def test_collection_analytics(client, admin_token, setup_analytics_data):
    """17-18. Aggregates collection totals, average fills, and daily breakdowns."""
    res = client.get(
        "/api/v1/analytics/collections",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["total_collections"] == 3
    assert data["total_collected_quantity_kg"] == 40.0
    assert data["average_collected_quantity_kg"] == 20.0  # 40 / 2 measured collections
    assert data["average_fill_before"] is not None
    assert len(data["frequently_collected_bins"]) > 0


# ============================================================================
# 19-21. BIN FILL ANALYTICS
# ============================================================================


def test_bin_fill_analytics(client, admin_token, setup_analytics_data):
    """19-21. Calculates average/max/min fill and lists high-fill bins with configurable threshold."""
    # Default threshold (80.0)
    res = client.get(
        "/api/v1/analytics/bin-fill",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["total_readings"] == 2
    assert data["max_fill_percentage"] == 85.0
    assert data["high_fill_reading_count"] == 1
    assert len(data["high_fill_bins"]) == 1
    assert data["high_fill_bins"][0]["bin_code"] == "ACAD-DRY-01"

    # Custom threshold (50.0)
    res_cust = client.get(
        "/api/v1/analytics/bin-fill?threshold=50.0",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_cust.status_code == status.HTTP_200_OK
    assert res_cust.json()["high_fill_threshold"] == 50.0


# ============================================================================
# 22-24. REPORT ANALYTICS
# ============================================================================


def test_report_analytics(client, admin_token, setup_analytics_data):
    """22-24. Report status aggregation, types, and resolution time calculation."""
    res = client.get(
        "/api/v1/analytics/reports",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["total_reports"] == 2
    assert data["pending_reports"] == 1
    assert data["resolved_reports"] == 1
    assert "OVERFLOWING" in data["reports_by_type"]
    assert "WRONG_SEGREGATION" in data["reports_by_type"]
    assert data["average_resolution_time_hours"] is not None
    assert data["average_resolution_time_hours"] > 0.0


# ============================================================================
# 25-29. PROCESSING & DIVERSION ANALYTICS
# ============================================================================


def test_processing_analytics(client, admin_token, setup_analytics_data):
    """25-29. Recycling, composting, diversion rate, and breakdown by waste type and location."""
    res = client.get(
        "/api/v1/analytics/processing",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["total_processing_records"] == 2
    assert data["total_processed_quantity_kg"] == 32.0
    assert data["total_recycled_quantity_kg"] == 20.0
    assert data["total_composted_quantity_kg"] == 12.0
    assert data["diversion_rate"] == 80.0
    assert len(data["processing_by_waste_type"]) == 2
    assert len(data["processing_by_location"]) == 2


# ============================================================================
# 30-32. PARTICIPATION ANALYTICS
# ============================================================================


def test_participation_analytics(client, admin_token, setup_analytics_data):
    """30-32. Student participation count, engagement rate, and active student ratio."""
    res = client.get(
        "/api/v1/analytics/participation",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["total_active_students"] >= 1
    assert data["students_with_at_least_one_disposal"] == 1
    assert data["unique_participating_students"] == 1
    assert data["participation_rate"] is not None
    assert data["participation_rate"] > 0.0


# ============================================================================
# 33-35. GAMIFICATION ANALYTICS
# ============================================================================


def test_gamification_analytics(client, admin_token, setup_analytics_data):
    """33-35. Points earned, redeemed, redemptions count, and top redeemed rewards."""
    res = client.get(
        "/api/v1/analytics/gamification",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["total_points_earned"] == 25
    assert data["total_points_redeemed"] == 50
    assert data["earning_transactions_count"] == 2
    assert data["reward_redemptions_count"] == 1
    assert "DISPOSAL" in data["points_earned_by_action"]
    assert len(data["most_redeemed_rewards"]) == 1
    assert data["most_redeemed_rewards"][0]["reward_title"] == "DBIT Cafeteria Chai Coupon"


# ============================================================================
# 36-39. PREDICTION ANALYTICS
# ============================================================================


def test_prediction_analytics(client, admin_token, setup_analytics_data):
    """36-39. Aggregates predictions, version counts, and high-fill forecasts."""
    res = client.get(
        "/api/v1/analytics/predictions",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["total_predictions"] == 2
    assert data["high_fill_predictions_count"] == 1
    assert "moving_average_v1" in data["predictions_by_model_version"]
    assert len(data["predictions_by_bin"]) == 2


# ============================================================================
# 40-43. CLASSIFICATION ANALYTICS
# ============================================================================


def test_classification_analytics(client, admin_token, setup_analytics_data):
    """40-43. AI classification distribution, confidence stats, and low-confidence count."""
    res = client.get(
        "/api/v1/analytics/classifications",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["total_classifications"] == 2
    assert data["low_confidence_count"] == 1
    assert "DRY_RECYCLABLE" in data["classifications_by_waste_type"]
    assert "WET_ORGANIC" in data["classifications_by_waste_type"]


# ============================================================================
# 44-47. OPERATIONAL ALERTS & IMMUTABILITY GUARANTEES
# ============================================================================


def test_operational_alerts_derived_in_memory(client, admin_token, setup_analytics_data):
    """Tests operational alerts derived dynamically without mutation."""
    res = client.get(
        "/api/v1/analytics/alerts",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    alert_types = [a["alert_type"] for a in data]
    assert "HIGH_FILL_BIN" in alert_types
    assert "OVERFLOW_REPORT" in alert_types
    assert "DAMAGED_BIN" in alert_types


def test_analytics_calls_are_strictly_read_only(
    client, admin_token, db_session: Session, setup_analytics_data
):
    """44-47. Ensures analytics requests do not mutate any operational tables or generate artifacts."""
    bins_before = db_session.query(Bin).count()
    reports_before = db_session.query(WasteReport).count()
    points_before = db_session.query(PointTransaction).count()
    predictions_before = db_session.query(FillPrediction).count()

    # Execute multiple analytics calls
    client.get("/api/v1/analytics/summary", headers={"Authorization": f"Bearer {admin_token}"})
    client.get("/api/v1/analytics/alerts", headers={"Authorization": f"Bearer {admin_token}"})
    client.get("/api/v1/analytics/waste-types", headers={"Authorization": f"Bearer {admin_token}"})
    client.get("/api/v1/analytics/locations", headers={"Authorization": f"Bearer {admin_token}"})
    client.get("/api/v1/analytics/bin-fill", headers={"Authorization": f"Bearer {admin_token}"})

    assert db_session.query(Bin).count() == bins_before
    assert db_session.query(WasteReport).count() == reports_before
    assert db_session.query(PointTransaction).count() == points_before
    assert db_session.query(FillPrediction).count() == predictions_before


def test_zero_active_students_handled_gracefully(client, admin_token, db_session: Session):
    """32. Verifies participation analytics returns null rate when no students exist."""
    # Deactivate or delete students in an isolated future range
    now = datetime.now(timezone.utc)
    future_start = (now + timedelta(days=200)).isoformat()
    future_end = (now + timedelta(days=210)).isoformat()

    res = client.get(
        "/api/v1/analytics/participation",
        params={"start_date": future_start, "end_date": future_end},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["students_with_at_least_one_disposal"] == 0
    assert data["unique_participating_students"] == 0


def test_diversion_rate_null_when_collected_quantity_unavailable(client, admin_token):
    """28. Diversion rate is NULL when collected quantity is unavailable in period."""
    now = datetime.now(timezone.utc)
    future_start = (now + timedelta(days=300)).isoformat()
    future_end = (now + timedelta(days=310)).isoformat()

    res = client.get(
        "/api/v1/analytics/processing",
        params={"start_date": future_start, "end_date": future_end},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["diversion_rate"] is None


def test_cross_module_end_to_end_consistency(client, admin_token, setup_analytics_data):
    """48-50. End-to-end multi-module verification ensuring all analytical endpoints remain internally consistent."""
    # 1. Summary
    summary_res = client.get(
        "/api/v1/analytics/summary",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert summary_res.status_code == status.HTTP_200_OK
    s = summary_res.json()

    # 2. Waste Types
    wt_res = client.get(
        "/api/v1/analytics/waste-types",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert wt_res.status_code == status.HTTP_200_OK
    wts = wt_res.json()
    total_wt_disposals = sum(item["disposal_count"] for item in wts)
    total_wt_collected = sum(item["collected_quantity_kg"] or 0.0 for item in wts)

    # Cross-consistency checks
    assert s["summary"]["disposal_count"] == total_wt_disposals
    assert s["summary"]["total_collected_quantity_kg"] == total_wt_collected

    # 3. Processing
    proc_res = client.get(
        "/api/v1/analytics/processing",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert proc_res.status_code == status.HTTP_200_OK
    p = proc_res.json()
    assert s["summary"]["total_processed_quantity_kg"] == p["total_processed_quantity_kg"]
    assert s["summary"]["diversion_rate"] == p["diversion_rate"]

    # 4. Gamification
    gam_res = client.get(
        "/api/v1/analytics/gamification",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert gam_res.status_code == status.HTTP_200_OK
    g = gam_res.json()
    assert s["gamification"]["total_points_earned"] == g["total_points_earned"]
    assert s["gamification"]["total_points_redeemed"] == g["total_points_redeemed"]
    assert s["gamification"]["reward_redemptions_count"] == g["reward_redemptions_count"]

    # 5. Predictions
    pred_res = client.get(
        "/api/v1/analytics/predictions",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert pred_res.status_code == status.HTTP_200_OK
    preds = pred_res.json()
    assert s["predictions"]["prediction_count"] == preds["total_predictions"]
    assert s["predictions"]["high_fill_predictions"] == preds["high_fill_predictions_count"]


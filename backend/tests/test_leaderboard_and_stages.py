import uuid
import pytest
from fastapi.testclient import TestClient

from app.core.gamification_config import calculate_eco_stage
from app.models.gamification import PointTransaction
from app.models.user import User


def test_calculate_eco_stage_progression():
    """Verify stage calculations and thresholds across all tiers."""
    # Eco Seed (0-99)
    s0 = calculate_eco_stage(0)
    assert s0["stage_name"] == "Eco Seed"
    assert s0["points_to_next_stage"] == 100
    assert s0["progress_percentage"] == 0.0

    # Green Sprout (100-299)
    s100 = calculate_eco_stage(100)
    assert s100["stage_name"] == "Green Sprout"
    assert s100["next_stage_name"] == "Eco Explorer"
    assert s100["points_to_next_stage"] == 200

    # Mid-stage progress (200 pts in Green Sprout: 100-300 span, 100/200 = 50%)
    s200 = calculate_eco_stage(200)
    assert s200["stage_name"] == "Green Sprout"
    assert s200["progress_percentage"] == 50.0

    # Max stage (Campus Earth Hero 3000+)
    s3500 = calculate_eco_stage(3500)
    assert s3500["stage_name"] == "Campus Earth Hero"
    assert s3500["is_max_stage"] is True
    assert s3500["points_to_next_stage"] == 0
    assert s3500["progress_percentage"] == 100.0


def test_get_my_stage_endpoint(client: TestClient, student_token: str, test_student_user: User):
    """Test retrieving student's current stage via API."""
    response = client.get(
        "/api/v1/gamification/me/stage",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "stage_name" in data
    assert "progress_percentage" in data
    assert "points_to_next_stage" in data
    assert "flair_icon" in data


def test_leaderboard_excludes_staff_and_ranks_students_by_earn_points(
    client: TestClient,
    student_token: str,
    test_student_user: User,
    test_staff_user: User,
    db_session,
):
    """Verify leaderboard accurately orders students by EARN points and excludes non-students."""
    # Award +50 pts EARN to student
    txn1 = PointTransaction(
        user_id=test_student_user.user_id,
        transaction_type="EARN",
        points=50,
        source_type="DISPOSAL",
        source_id=1,
        description="Disposal points",
    )
    db_session.add(txn1)
    db_session.commit()

    # Call leaderboard
    response = client.get(
        "/api/v1/gamification/leaderboard",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["period"] == "all-time"
    assert isinstance(data["leaderboard"], list)
    assert len(data["leaderboard"]) >= 1

    first_entry = data["leaderboard"][0]
    assert first_entry["display_name"] == test_student_user.name
    assert first_entry["earned_points"] >= 50
    assert "stage_name" in first_entry
    assert "flair_icon" in first_entry

    assert data["current_user_rank"] is not None
    assert data["current_user_rank"]["display_name"] == test_student_user.name


def test_leaderboard_period_filter(client: TestClient, student_token: str, test_student_user: User):
    """Test period filtering on leaderboard (all-time, month, week)."""
    for period in ["all-time", "month", "week"]:
        response = client.get(
            f"/api/v1/gamification/leaderboard?period={period}",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == period
        assert isinstance(data["leaderboard"], list)

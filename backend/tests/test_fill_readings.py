import uuid
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.bin import Bin


def test_collector_can_create_fill_reading(
    client: TestClient,
    collector_token: str,
    test_bin: Bin,
) -> None:
    response = client.post(
        f"/api/v1/bins/{test_bin.bin_id}/fill-readings",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={
            "fill_percentage": "78.50",
            "source": "MANUAL",
            "notes": "Visual manual inspection",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["bin_id"] == str(test_bin.bin_id)
    assert float(data["fill_percentage"]) == 78.50
    assert data["source"] == "MANUAL"
    assert data["notes"] == "Visual manual inspection"
    assert "reading_id" in data
    assert "recorded_at" in data

    # Verify that the bin's current_fill_percentage was updated
    bin_res = client.get(
        f"/api/v1/bins/{test_bin.bin_id}",
        headers={"Authorization": f"Bearer {collector_token}"},
    )
    assert bin_res.status_code == 200
    assert float(bin_res.json()["current_fill_percentage"]) == 78.50


def test_admin_can_create_fill_reading(
    client: TestClient,
    admin_token: str,
    test_bin: Bin,
) -> None:
    response = client.post(
        f"/api/v1/bins/{test_bin.bin_id}/fill-readings",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "fill_percentage": "25.00",
            "source": "MANUAL",
        },
    )
    assert response.status_code == 201
    assert float(response.json()["fill_percentage"]) == 25.00


def test_student_and_staff_cannot_create_fill_reading(
    client: TestClient,
    student_token: str,
    staff_token: str,
    test_bin: Bin,
) -> None:
    for token in [student_token, staff_token]:
        response = client.post(
            f"/api/v1/bins/{test_bin.bin_id}/fill-readings",
            headers={"Authorization": f"Bearer {token}"},
            json={"fill_percentage": "50.00"},
        )
        assert response.status_code == 403


def test_unauthenticated_cannot_create_fill_reading(
    client: TestClient,
    test_bin: Bin,
) -> None:
    response = client.post(
        f"/api/v1/bins/{test_bin.bin_id}/fill-readings",
        json={"fill_percentage": "50.00"},
    )
    assert response.status_code == 401


def test_fill_reading_nonexistent_bin_returns_404(
    client: TestClient,
    collector_token: str,
) -> None:
    fake_bin = uuid.uuid4()
    response = client.post(
        f"/api/v1/bins/{fake_bin}/fill-readings",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"fill_percentage": "50.00"},
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_valid_boundary_fill_percentages_accepted(
    client: TestClient,
    collector_token: str,
    test_bin: Bin,
) -> None:
    for fill_val in ["0.00", "100.00"]:
        response = client.post(
            f"/api/v1/bins/{test_bin.bin_id}/fill-readings",
            headers={"Authorization": f"Bearer {collector_token}"},
            json={"fill_percentage": fill_val},
        )
        assert response.status_code == 201
        assert float(response.json()["fill_percentage"]) == float(fill_val)


def test_invalid_fill_percentages_rejected(
    client: TestClient,
    collector_token: str,
    test_bin: Bin,
) -> None:
    for invalid_val in ["-0.01", "100.01", "150.00", "-50"]:
        response = client.post(
            f"/api/v1/bins/{test_bin.bin_id}/fill-readings",
            headers={"Authorization": f"Bearer {collector_token}"},
            json={"fill_percentage": invalid_val},
        )
        assert response.status_code == 422


def test_invalid_source_rejected(
    client: TestClient,
    collector_token: str,
    test_bin: Bin,
) -> None:
    response = client.post(
        f"/api/v1/bins/{test_bin.bin_id}/fill-readings",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={
            "fill_percentage": "50.00",
            "source": "INVALID_SOURCE",
        },
    )
    assert response.status_code == 422


def test_list_historical_fill_readings(
    client: TestClient,
    collector_token: str,
    student_token: str,
    test_bin: Bin,
) -> None:
    # 1. Create multiple readings
    client.post(
        f"/api/v1/bins/{test_bin.bin_id}/fill-readings",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"fill_percentage": "30.00", "notes": "Morning"},
    )
    client.post(
        f"/api/v1/bins/{test_bin.bin_id}/fill-readings",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"fill_percentage": "60.00", "notes": "Afternoon"},
    )
    client.post(
        f"/api/v1/bins/{test_bin.bin_id}/fill-readings",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"fill_percentage": "90.00", "notes": "Evening"},
    )

    # 2. List readings for this bin
    res = client.get(
        f"/api/v1/bins/{test_bin.bin_id}/fill-readings",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 200
    readings = res.json()
    assert len(readings) >= 3
    notes = [r["notes"] for r in readings]
    assert "Morning" in notes
    assert "Afternoon" in notes
    assert "Evening" in notes


def test_get_fill_reading_by_id(
    client: TestClient,
    collector_token: str,
    test_bin: Bin,
) -> None:
    create_res = client.post(
        f"/api/v1/bins/{test_bin.bin_id}/fill-readings",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"fill_percentage": "42.00", "notes": "Specific lookup"},
    )
    reading_id = create_res.json()["reading_id"]

    get_res = client.get(
        f"/api/v1/fill-readings/{reading_id}",
        headers={"Authorization": f"Bearer {collector_token}"},
    )
    assert get_res.status_code == 200
    assert get_res.json()["reading_id"] == reading_id
    assert float(get_res.json()["fill_percentage"]) == 42.00


def test_historical_fill_readings_cannot_be_modified(
    client: TestClient,
    admin_token: str,
    test_bin: Bin,
) -> None:
    create_res = client.post(
        f"/api/v1/bins/{test_bin.bin_id}/fill-readings",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"fill_percentage": "50.00"},
    )
    reading_id = create_res.json()["reading_id"]

    patch_res = client.patch(
        f"/api/v1/fill-readings/{reading_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"fill_percentage": "70.00"},
    )
    assert patch_res.status_code in [404, 405]

    delete_res = client.delete(
        f"/api/v1/fill-readings/{reading_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert delete_res.status_code in [404, 405]

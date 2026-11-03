import uuid
from fastapi.testclient import TestClient
from app.models.bin import Bin
from app.models.location import Location
from app.models.waste_type import WasteType


def test_admin_can_create_bin(
    client: TestClient,
    admin_token: str,
    test_location: Location,
    test_waste_type: WasteType,
) -> None:
    response = client.post(
        "/api/v1/bins",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "bin_code": "CANTEEN-DRY-01",
            "location_id": test_location.location_id,
            "waste_type_id": test_waste_type.waste_type_id,
            "capacity_litres": "80.00",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["bin_code"] == "CANTEEN-DRY-01"
    assert data["location"]["location_id"] == test_location.location_id
    assert data["waste_type"]["waste_type_id"] == test_waste_type.waste_type_id
    assert data["status"] == "ACTIVE"
    assert "bin_id" in data
    assert "qr_token" in data


def test_non_admin_cannot_create_bin(
    client: TestClient,
    student_token: str,
    test_location: Location,
    test_waste_type: WasteType,
) -> None:
    response = client.post(
        "/api/v1/bins",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "bin_code": "STUDENT-BIN-01",
            "location_id": test_location.location_id,
            "waste_type_id": test_waste_type.waste_type_id,
        },
    )
    assert response.status_code == 403


def test_duplicate_bin_code_rejected(
    client: TestClient,
    admin_token: str,
    test_bin: Bin,
    test_location: Location,
    test_waste_type: WasteType,
) -> None:
    response = client.post(
        "/api/v1/bins",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "bin_code": test_bin.bin_code,
            "location_id": test_location.location_id,
            "waste_type_id": test_waste_type.waste_type_id,
        },
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


def test_create_bin_with_nonexistent_location_rejected(
    client: TestClient,
    admin_token: str,
    test_waste_type: WasteType,
) -> None:
    response = client.post(
        "/api/v1/bins",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "bin_code": "INVALID-LOC-BIN",
            "location_id": 99999,
            "waste_type_id": test_waste_type.waste_type_id,
        },
    )
    assert response.status_code == 404
    assert "location with id 99999 not found" in response.json()["detail"].lower()


def test_create_bin_with_nonexistent_waste_type_rejected(
    client: TestClient,
    admin_token: str,
    test_location: Location,
) -> None:
    response = client.post(
        "/api/v1/bins",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "bin_code": "INVALID-WT-BIN",
            "location_id": test_location.location_id,
            "waste_type_id": 99999,
        },
    )
    assert response.status_code == 404
    assert "waste type with id 99999 not found" in response.json()["detail"].lower()


def test_authenticated_user_can_list_bins(
    client: TestClient,
    student_token: str,
    test_bin: Bin,
) -> None:
    response = client.get(
        "/api/v1/bins",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(b["bin_code"] == test_bin.bin_code for b in data)


def test_authenticated_user_can_view_bin_by_id(
    client: TestClient,
    student_token: str,
    test_bin: Bin,
) -> None:
    response = client.get(
        f"/api/v1/bins/{test_bin.bin_id}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["bin_id"] == str(test_bin.bin_id)
    assert data["bin_code"] == test_bin.bin_code
    assert data["location"]["name"] == test_bin.location.name
    assert data["waste_type"]["name"] == test_bin.waste_type.name


def test_admin_can_update_bin(
    client: TestClient,
    admin_token: str,
    test_bin: Bin,
) -> None:
    response = client.patch(
        f"/api/v1/bins/{test_bin.bin_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "current_fill_percentage": "85.00",
            "status": "FULL",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert float(data["current_fill_percentage"]) == 85.0
    assert data["status"] == "FULL"


def test_invalid_bin_status_update_rejected(
    client: TestClient,
    admin_token: str,
    test_bin: Bin,
) -> None:
    response = client.patch(
        f"/api/v1/bins/{test_bin.bin_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "INVALID_STATUS"},
    )
    assert response.status_code == 422


def test_invalid_fill_percentage_update_rejected(
    client: TestClient,
    admin_token: str,
    test_bin: Bin,
) -> None:
    response = client.patch(
        f"/api/v1/bins/{test_bin.bin_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"current_fill_percentage": "150.00"},
    )
    assert response.status_code == 422


def test_qr_lookup_authenticated(
    client: TestClient,
    student_token: str,
    test_bin: Bin,
) -> None:
    response = client.get(
        f"/api/v1/bins/qr/{test_bin.qr_token}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["bin_id"] == str(test_bin.bin_id)
    assert data["bin_code"] == test_bin.bin_code
    assert data["location"]["name"] == test_bin.location.name
    assert data["waste_type"]["name"] == test_bin.waste_type.name
    assert data["status"] == test_bin.status
    assert float(data["current_fill_percentage"]) == float(test_bin.current_fill_percentage)


def test_qr_lookup_invalid_token_returns_404(
    client: TestClient,
    student_token: str,
) -> None:
    fake_token = uuid.uuid4()
    response = client.get(
        f"/api/v1/bins/qr/{fake_token}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_qr_lookup_unauthenticated_returns_401(
    client: TestClient,
    test_bin: Bin,
) -> None:
    response = client.get(f"/api/v1/bins/qr/{test_bin.qr_token}")
    assert response.status_code == 401


def test_bin_filtering_by_location_and_status(
    client: TestClient,
    student_token: str,
    test_bin: Bin,
) -> None:
    # Filter by location_id
    response = client.get(
        f"/api/v1/bins?location_id={test_bin.location_id}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # Filter by non-matching location_id
    response_empty = client.get(
        "/api/v1/bins?location_id=99999",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response_empty.status_code == 200
    assert len(response_empty.json()) == 0


def test_end_to_end_qr_lookup_workflow(
    client: TestClient,
    admin_token: str,
    student_token: str,
    test_waste_type: WasteType,
) -> None:
    # 1. Admin creates a new location
    loc_res = client.post(
        "/api/v1/locations",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "DBIT Amphitheatre",
            "location_type": "OUTDOOR",
            "building": "Central Plaza",
            "floor": "Ground Floor",
        },
    )
    assert loc_res.status_code == 201
    loc_id = loc_res.json()["location_id"]

    # 2. Admin creates a bin in this location
    bin_res = client.post(
        "/api/v1/bins",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "bin_code": "AMPHI-WET-01",
            "location_id": loc_id,
            "waste_type_id": test_waste_type.waste_type_id,
            "capacity_litres": "100.00",
        },
    )
    assert bin_res.status_code == 201
    bin_data = bin_res.json()
    qr_token = bin_data["qr_token"]

    # 3. Student scans QR code and performs QR lookup
    qr_res = client.get(
        f"/api/v1/bins/qr/{qr_token}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert qr_res.status_code == 200
    qr_data = qr_res.json()
    assert qr_data["bin_code"] == "AMPHI-WET-01"
    assert qr_data["location"]["name"] == "DBIT Amphitheatre"
    assert qr_data["waste_type"]["name"] == "WET_ORGANIC"
    assert qr_data["status"] == "ACTIVE"


def test_public_qr_lookup_unauthenticated(
    client: TestClient,
    test_bin: Bin,
) -> None:
    response = client.get(f"/api/v1/bins/public/{test_bin.qr_token}")
    assert response.status_code == 200
    data = response.json()
    assert data["bin_id"] == str(test_bin.bin_id)
    assert data["bin_code"] == test_bin.bin_code
    assert data["location"]["name"] == test_bin.location.name
    assert data["waste_type"]["name"] == test_bin.waste_type.name
    assert data["status"] == test_bin.status
    assert float(data["current_fill_percentage"]) == float(test_bin.current_fill_percentage)


def test_public_qr_lookup_invalid_token_returns_404(
    client: TestClient,
) -> None:
    fake_token = uuid.uuid4()
    response = client.get(f"/api/v1/bins/public/{fake_token}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_public_qr_lookup_safe_fields_only(
    client: TestClient,
    test_bin: Bin,
) -> None:
    response = client.get(f"/api/v1/bins/public/{test_bin.qr_token}")
    assert response.status_code == 200
    data = response.json()
    # Ensure sensitive or internal administrative fields are NOT present
    assert "qr_token" not in data
    assert "created_at" not in data
    assert "updated_at" not in data
    assert "installed_at" not in data
    # Ensure public-safe fields ARE present
    assert "bin_id" in data
    assert "bin_code" in data
    assert "location" in data
    assert "waste_type" in data
    assert "capacity_litres" in data
    assert "current_fill_percentage" in data
    assert "status" in data

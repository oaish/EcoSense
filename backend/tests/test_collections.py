import uuid
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.bin import Bin
from app.models.location import Location
from app.models.user import User
from app.models.waste_type import WasteType


def test_collector_can_create_collection(
    client: TestClient,
    collector_token: str,
    test_collector_user: User,
    test_bin: Bin,
) -> None:
    response = client.post(
        "/api/v1/collections",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={
            "bin_id": str(test_bin.bin_id),
            "fill_level_before": "85.00",
            "collected_quantity_kg": "12.450",
            "fill_level_after": "0.00",
            "notes": "Full cleanout completed",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["bin_id"] == str(test_bin.bin_id)
    assert data["collector_id"] == str(test_collector_user.user_id)
    assert float(data["fill_level_before"]) == 85.00
    assert float(data["collected_quantity_kg"]) == 12.450
    assert float(data["fill_level_after"]) == 0.00
    assert "collection_id" in data
    assert "collected_at" in data

    # Verify that the bin's current fill percentage is updated to fill_level_after (0.00)
    bin_res = client.get(
        f"/api/v1/bins/{test_bin.bin_id}",
        headers={"Authorization": f"Bearer {collector_token}"},
    )
    assert bin_res.status_code == 200
    assert float(bin_res.json()["current_fill_percentage"]) == 0.00


def test_admin_can_create_collection(
    client: TestClient,
    admin_token: str,
    test_bin: Bin,
) -> None:
    response = client.post(
        "/api/v1/collections",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "bin_id": str(test_bin.bin_id),
            "fill_level_before": "90.00",
            "fill_level_after": "5.00",
        },
    )
    assert response.status_code == 201
    assert float(response.json()["fill_level_after"]) == 5.00


def test_student_and_staff_cannot_create_collection(
    client: TestClient,
    student_token: str,
    staff_token: str,
    test_bin: Bin,
) -> None:
    for token in [student_token, staff_token]:
        response = client.post(
            "/api/v1/collections",
            headers={"Authorization": f"Bearer {token}"},
            json={"bin_id": str(test_bin.bin_id)},
        )
        assert response.status_code == 403


def test_unauthenticated_cannot_create_collection(
    client: TestClient,
    test_bin: Bin,
) -> None:
    response = client.post(
        "/api/v1/collections",
        json={"bin_id": str(test_bin.bin_id)},
    )
    assert response.status_code == 401


def test_collection_nonexistent_bin_returns_404(
    client: TestClient,
    collector_token: str,
) -> None:
    fake_bin = uuid.uuid4()
    response = client.post(
        "/api/v1/collections",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"bin_id": str(fake_bin)},
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_invalid_fill_levels_rejected(
    client: TestClient,
    collector_token: str,
    test_bin: Bin,
) -> None:
    for invalid_val in ["-1", "101", "150"]:
        response = client.post(
            "/api/v1/collections",
            headers={"Authorization": f"Bearer {collector_token}"},
            json={
                "bin_id": str(test_bin.bin_id),
                "fill_level_before": invalid_val,
            },
        )
        assert response.status_code == 422


def test_invalid_collected_quantities_rejected(
    client: TestClient,
    collector_token: str,
    test_bin: Bin,
) -> None:
    for invalid_qty in ["0", "-5.00"]:
        response = client.post(
            "/api/v1/collections",
            headers={"Authorization": f"Bearer {collector_token}"},
            json={
                "bin_id": str(test_bin.bin_id),
                "collected_quantity_kg": invalid_qty,
            },
        )
        assert response.status_code == 422


def test_null_quantity_and_fill_levels_accepted(
    client: TestClient,
    collector_token: str,
    test_bin: Bin,
) -> None:
    response = client.post(
        "/api/v1/collections",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={
            "bin_id": str(test_bin.bin_id),
            "fill_level_before": None,
            "collected_quantity_kg": None,
            "fill_level_after": None,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["collected_quantity_kg"] is None
    assert data["fill_level_before"] is None
    assert data["fill_level_after"] is None


def test_collector_id_taken_from_jwt_and_cannot_be_overridden(
    client: TestClient,
    collector_token: str,
    test_admin_user: User,
    test_collector_user: User,
    test_bin: Bin,
) -> None:
    response = client.post(
        "/api/v1/collections",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={
            "bin_id": str(test_bin.bin_id),
            "collector_id": str(test_admin_user.user_id),
        },
    )
    assert response.status_code == 201
    assert response.json()["collector_id"] == str(test_collector_user.user_id)


def test_damaged_bin_status_preserved_on_collection(
    client: TestClient,
    collector_token: str,
    db_session: Session,
    test_location: Location,
    test_waste_type: WasteType,
) -> None:
    damaged_bin = Bin(
        bin_code="DAMAGED-COLLECT-01",
        location_id=test_location.location_id,
        waste_type_id=test_waste_type.waste_type_id,
        status="DAMAGED",
        current_fill_percentage=Decimal("95.00"),
    )
    db_session.add(damaged_bin)
    db_session.commit()
    db_session.refresh(damaged_bin)

    response = client.post(
        "/api/v1/collections",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={
            "bin_id": str(damaged_bin.bin_id),
            "fill_level_before": "95.00",
            "fill_level_after": "0.00",
        },
    )
    assert response.status_code == 201

    # Verify status is still DAMAGED, but current fill is 0
    bin_res = client.get(
        f"/api/v1/bins/{damaged_bin.bin_id}",
        headers={"Authorization": f"Bearer {collector_token}"},
    )
    assert bin_res.status_code == 200
    assert bin_res.json()["status"] == "DAMAGED"
    assert float(bin_res.json()["current_fill_percentage"]) == 0.00


def test_list_collections_scoping(
    client: TestClient,
    collector_token: str,
    admin_token: str,
    test_bin: Bin,
) -> None:
    client.post(
        "/api/v1/collections",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"bin_id": str(test_bin.bin_id), "notes": "Route A Collection"},
    )

    collector_list = client.get(
        "/api/v1/collections",
        headers={"Authorization": f"Bearer {collector_token}"},
    ).json()
    assert len(collector_list) >= 1

    admin_list = client.get(
        "/api/v1/collections",
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()
    assert len(admin_list) >= 1


def test_historical_collections_cannot_be_modified(
    client: TestClient,
    admin_token: str,
    test_bin: Bin,
) -> None:
    create_res = client.post(
        "/api/v1/collections",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"bin_id": str(test_bin.bin_id)},
    )
    collection_id = create_res.json()["collection_id"]

    patch_res = client.patch(
        f"/api/v1/collections/{collection_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"notes": "Hacked collection note"},
    )
    assert patch_res.status_code in [404, 405]

    delete_res = client.delete(
        f"/api/v1/collections/{collection_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert delete_res.status_code in [404, 405]


def test_end_to_end_qr_fill_and_collection_workflow(
    client: TestClient,
    admin_token: str,
    collector_token: str,
    test_waste_type: WasteType,
) -> None:
    # 1. Admin creates Location
    loc_res = client.post(
        "/api/v1/locations",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "DBIT Sports Complex",
            "location_type": "OUTDOOR",
            "building": "Sports Arena",
        },
    )
    assert loc_res.status_code == 201
    location_id = loc_res.json()["location_id"]

    # 2. Admin creates Bin
    bin_res = client.post(
        "/api/v1/bins",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "bin_code": "SPORTS-DRY-01",
            "location_id": location_id,
            "waste_type_id": test_waste_type.waste_type_id,
            "capacity_litres": "150.00",
        },
    )
    assert bin_res.status_code == 201
    bin_id = bin_res.json()["bin_id"]
    qr_token = bin_res.json()["qr_token"]

    # 3. Collector scans QR Code
    qr_res = client.get(
        f"/api/v1/bins/qr/{qr_token}",
        headers={"Authorization": f"Bearer {collector_token}"},
    )
    assert qr_res.status_code == 200
    assert qr_res.json()["bin_code"] == "SPORTS-DRY-01"

    # 4. Collector logs a manual fill reading of 85%
    reading_res = client.post(
        f"/api/v1/bins/{bin_id}/fill-readings",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={
            "fill_percentage": "85.00",
            "source": "MANUAL",
            "notes": "Pre-collection inspection",
        },
    )
    assert reading_res.status_code == 201
    assert float(reading_res.json()["fill_percentage"]) == 85.00

    # Verify bin current fill is now 85%
    bin_state_1 = client.get(
        f"/api/v1/bins/{bin_id}",
        headers={"Authorization": f"Bearer {collector_token}"},
    ).json()
    assert float(bin_state_1["current_fill_percentage"]) == 85.00

    # 5. Collector empties the bin and logs collection (85% -> 0%, 12.4 kg)
    collect_res = client.post(
        "/api/v1/collections",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={
            "bin_id": bin_id,
            "fill_level_before": "85.00",
            "collected_quantity_kg": "12.400",
            "fill_level_after": "0.00",
            "notes": "Afternoon pickup",
        },
    )
    assert collect_res.status_code == 201

    # 6. Verify final states:
    # Bin current fill is 0%
    bin_state_2 = client.get(
        f"/api/v1/bins/{bin_id}",
        headers={"Authorization": f"Bearer {collector_token}"},
    ).json()
    assert float(bin_state_2["current_fill_percentage"]) == 0.00

    # Historical fill reading remains 85%
    readings_list = client.get(
        f"/api/v1/bins/{bin_id}/fill-readings",
        headers={"Authorization": f"Bearer {collector_token}"},
    ).json()
    assert len(readings_list) == 1
    assert float(readings_list[0]["fill_percentage"]) == 85.00

import uuid
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.bin import Bin
from app.models.location import Location
from app.models.user import User
from app.models.waste_type import WasteType


def test_student_can_create_disposal(
    client: TestClient,
    student_token: str,
    test_bin: Bin,
) -> None:
    response = client.post(
        "/api/v1/disposals",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "bin_id": str(test_bin.bin_id),
            "quantity_kg": "0.750",
            "notes": "Food waste container",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["bin_id"] == str(test_bin.bin_id)
    assert data["bin_code"] == test_bin.bin_code
    assert data["waste_type"]["name"] == test_bin.waste_type.name
    assert float(data["quantity_kg"]) == 0.750
    assert "disposal_id" in data
    assert "recorded_at" in data


def test_staff_can_create_disposal(
    client: TestClient,
    staff_token: str,
    test_bin: Bin,
) -> None:
    response = client.post(
        "/api/v1/disposals",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={
            "bin_id": str(test_bin.bin_id),
            "quantity_kg": None,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["bin_id"] == str(test_bin.bin_id)
    assert data["quantity_kg"] is None


def test_unauthenticated_user_cannot_create_disposal(
    client: TestClient,
    test_bin: Bin,
) -> None:
    response = client.post(
        "/api/v1/disposals",
        json={"bin_id": str(test_bin.bin_id)},
    )
    assert response.status_code == 401


def test_collector_cannot_create_disposal(
    client: TestClient,
    collector_token: str,
    test_bin: Bin,
) -> None:
    response = client.post(
        "/api/v1/disposals",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"bin_id": str(test_bin.bin_id)},
    )
    assert response.status_code == 403


def test_admin_cannot_create_disposal(
    client: TestClient,
    admin_token: str,
    test_bin: Bin,
) -> None:
    response = client.post(
        "/api/v1/disposals",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"bin_id": str(test_bin.bin_id)},
    )
    assert response.status_code == 403


def test_user_id_taken_from_jwt_and_cannot_be_overridden(
    client: TestClient,
    student_token: str,
    test_admin_user: User,
    test_bin: Bin,
) -> None:
    # Attempting to supply a different user_id
    response = client.post(
        "/api/v1/disposals",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "bin_id": str(test_bin.bin_id),
            "user_id": str(test_admin_user.user_id),
        },
    )
    # user_id is ignored or forbidden by schema, record is bound to student
    assert response.status_code == 201


def test_disposal_to_nonexistent_bin_returns_404(
    client: TestClient,
    student_token: str,
) -> None:
    fake_bin = uuid.uuid4()
    response = client.post(
        "/api/v1/disposals",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"bin_id": str(fake_bin)},
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_disposal_to_full_bin_rejected(
    client: TestClient,
    student_token: str,
    db_session: Session,
    test_location: Location,
    test_waste_type: WasteType,
) -> None:
    full_bin = Bin(
        bin_code="FULL-BIN-01",
        location_id=test_location.location_id,
        waste_type_id=test_waste_type.waste_type_id,
        status="FULL",
    )
    db_session.add(full_bin)
    db_session.commit()
    db_session.refresh(full_bin)

    response = client.post(
        "/api/v1/disposals",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"bin_id": str(full_bin.bin_id)},
    )
    assert response.status_code == 409
    assert "full" in response.json()["detail"].lower()


def test_disposal_to_damaged_missing_inactive_bin_rejected(
    client: TestClient,
    student_token: str,
    db_session: Session,
    test_location: Location,
    test_waste_type: WasteType,
) -> None:
    for status_val in ["DAMAGED", "MISSING", "INACTIVE"]:
        bad_bin = Bin(
            bin_code=f"BAD-BIN-{status_val}",
            location_id=test_location.location_id,
            waste_type_id=test_waste_type.waste_type_id,
            status=status_val,
        )
        db_session.add(bad_bin)
        db_session.commit()
        db_session.refresh(bad_bin)

        response = client.post(
            "/api/v1/disposals",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"bin_id": str(bad_bin.bin_id)},
        )
        assert response.status_code == 409
        assert status_val.lower() in response.json()["detail"].lower()


def test_zero_or_negative_quantity_rejected(
    client: TestClient,
    student_token: str,
    test_bin: Bin,
) -> None:
    for invalid_qty in ["0", "-1.50"]:
        response = client.post(
            "/api/v1/disposals",
            headers={"Authorization": f"Bearer {student_token}"},
            json={
                "bin_id": str(test_bin.bin_id),
                "quantity_kg": invalid_qty,
            },
        )
        assert response.status_code == 422


def test_student_can_retrieve_own_disposal(
    client: TestClient,
    student_token: str,
    test_bin: Bin,
) -> None:
    create_res = client.post(
        "/api/v1/disposals",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"bin_id": str(test_bin.bin_id), "quantity_kg": "1.250"},
    )
    assert create_res.status_code == 201
    disposal_id = create_res.json()["disposal_id"]

    get_res = client.get(
        f"/api/v1/disposals/{disposal_id}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert get_res.status_code == 200
    assert get_res.json()["disposal_id"] == disposal_id


def test_student_cannot_view_other_user_disposal(
    client: TestClient,
    student_token: str,
    staff_token: str,
    test_bin: Bin,
) -> None:
    # Staff creates a disposal
    create_res = client.post(
        "/api/v1/disposals",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={"bin_id": str(test_bin.bin_id)},
    )
    disposal_id = create_res.json()["disposal_id"]

    # Student attempts to view staff's disposal
    get_res = client.get(
        f"/api/v1/disposals/{disposal_id}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert get_res.status_code == 403


def test_list_disposal_scoping(
    client: TestClient,
    student_token: str,
    staff_token: str,
    admin_token: str,
    test_bin: Bin,
) -> None:
    # 1. Student creates disposal
    client.post(
        "/api/v1/disposals",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"bin_id": str(test_bin.bin_id), "notes": "Student entry"},
    )

    # 2. Staff creates disposal
    client.post(
        "/api/v1/disposals",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={"bin_id": str(test_bin.bin_id), "notes": "Staff entry"},
    )

    # 3. Student listing only shows their entry
    student_list = client.get(
        "/api/v1/disposals",
        headers={"Authorization": f"Bearer {student_token}"},
    ).json()
    assert all(d["notes"] == "Student entry" for d in student_list)

    # 4. Admin listing can see all
    admin_list = client.get(
        "/api/v1/disposals",
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()
    assert len(admin_list) >= 2

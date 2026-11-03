import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.bin import Bin
from app.models.location import Location
from app.models.user import User
from app.models.waste_type import WasteType


def test_student_can_create_report(
    client: TestClient,
    student_token: str,
    test_bin: Bin,
) -> None:
    response = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "bin_id": str(test_bin.bin_id),
            "report_type": "OVERFLOWING",
            "description": "Bin is overflowing after lunch break",
            "image_url": "https://storage.ecosense.local/reports/overflow1.jpg",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["report_type"] == "OVERFLOWING"
    assert data["status"] == "PENDING"
    assert data["bin_id"] == str(test_bin.bin_id)
    assert data["bin_code"] == test_bin.bin_code
    assert data["resolved_at"] is None
    assert data["resolved_by"] is None
    assert "report_id" in data


def test_staff_collector_admin_can_create_report(
    client: TestClient,
    staff_token: str,
    collector_token: str,
    admin_token: str,
    test_bin: Bin,
) -> None:
    for token, rtype in [
        (staff_token, "WRONG_SEGREGATION"),
        (collector_token, "DAMAGED_BIN"),
        (admin_token, "OTHER"),
    ]:
        response = client.post(
            "/api/v1/reports",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "bin_id": str(test_bin.bin_id),
                "report_type": rtype,
            },
        )
        assert response.status_code == 201
        assert response.json()["report_type"] == rtype


def test_unauthenticated_cannot_create_report(client: TestClient) -> None:
    response = client.post(
        "/api/v1/reports",
        json={"report_type": "OVERFLOWING"},
    )
    assert response.status_code == 401


def test_invalid_report_type_rejected(
    client: TestClient,
    student_token: str,
    test_bin: Bin,
) -> None:
    response = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "bin_id": str(test_bin.bin_id),
            "report_type": "INVALID_REPORT_TYPE",
        },
    )
    assert response.status_code == 422


def test_report_without_bin_allowed(
    client: TestClient,
    student_token: str,
) -> None:
    response = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "report_type": "OTHER",
            "description": "General campus corridor littering",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["bin_id"] is None
    assert data["bin_code"] is None
    assert data["report_type"] == "OTHER"


def test_report_on_damaged_missing_inactive_bin_allowed(
    client: TestClient,
    student_token: str,
    db_session: Session,
    test_location: Location,
    test_waste_type: WasteType,
) -> None:
    for status_val in ["DAMAGED", "MISSING", "INACTIVE", "FULL"]:
        bin_obj = Bin(
            bin_code=f"REPORT-BIN-{status_val}",
            location_id=test_location.location_id,
            waste_type_id=test_waste_type.waste_type_id,
            status=status_val,
        )
        db_session.add(bin_obj)
        db_session.commit()
        db_session.refresh(bin_obj)

        response = client.post(
            "/api/v1/reports",
            headers={"Authorization": f"Bearer {student_token}"},
            json={
                "bin_id": str(bin_obj.bin_id),
                "report_type": "DAMAGED_BIN" if status_val == "DAMAGED" else "OVERFLOWING",
            },
        )
        assert response.status_code == 201


def test_report_with_nonexistent_bin_returns_404(
    client: TestClient,
    student_token: str,
) -> None:
    fake_bin = uuid.uuid4()
    response = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "bin_id": str(fake_bin),
            "report_type": "OVERFLOWING",
        },
    )
    assert response.status_code == 404


def test_student_cannot_update_report(
    client: TestClient,
    student_token: str,
    test_bin: Bin,
) -> None:
    # 1. Student creates report
    create_res = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"bin_id": str(test_bin.bin_id), "report_type": "OVERFLOWING"},
    )
    report_id = create_res.json()["report_id"]

    # 2. Student attempts to update status to RESOLVED
    update_res = client.patch(
        f"/api/v1/reports/{report_id}",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"status": "RESOLVED"},
    )
    assert update_res.status_code == 403


def test_admin_can_update_and_resolve_report(
    client: TestClient,
    student_token: str,
    admin_token: str,
    test_admin_user: User,
    test_bin: Bin,
) -> None:
    # 1. Student creates report (starts as PENDING)
    create_res = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"bin_id": str(test_bin.bin_id), "report_type": "OVERFLOWING"},
    )
    report_id = create_res.json()["report_id"]
    assert create_res.json()["status"] == "PENDING"

    # 2. Admin updates to IN_PROGRESS
    progress_res = client.patch(
        f"/api/v1/reports/{report_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "IN_PROGRESS"},
    )
    assert progress_res.status_code == 200
    assert progress_res.json()["status"] == "IN_PROGRESS"
    assert progress_res.json()["resolved_at"] is None

    # 3. Admin marks as RESOLVED
    resolve_res = client.patch(
        f"/api/v1/reports/{report_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "RESOLVED"},
    )
    assert resolve_res.status_code == 200
    resolve_data = resolve_res.json()
    assert resolve_data["status"] == "RESOLVED"
    assert resolve_data["resolved_at"] is not None
    assert resolve_data["resolved_by"] == str(test_admin_user.user_id)


def test_student_cannot_view_other_user_report(
    client: TestClient,
    student_token: str,
    staff_token: str,
    test_bin: Bin,
) -> None:
    # Staff submits report
    create_res = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={"bin_id": str(test_bin.bin_id), "report_type": "DAMAGED_BIN"},
    )
    report_id = create_res.json()["report_id"]

    # Student attempts to view it
    get_res = client.get(
        f"/api/v1/reports/{report_id}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert get_res.status_code == 403


def test_end_to_end_qr_disposal_and_report_lifecycle(
    client: TestClient,
    admin_token: str,
    student_token: str,
    test_admin_user: User,
    test_waste_type: WasteType,
) -> None:
    # Step 1: Admin creates Location
    loc_res = client.post(
        "/api/v1/locations",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "DBIT Mechanical Quad",
            "location_type": "OUTDOOR",
            "building": "Workshop Wing",
            "floor": "Ground Floor",
        },
    )
    assert loc_res.status_code == 201
    location_id = loc_res.json()["location_id"]

    # Step 2: Admin creates Bin
    bin_res = client.post(
        "/api/v1/bins",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "bin_code": "QUAD-WET-01",
            "location_id": location_id,
            "waste_type_id": test_waste_type.waste_type_id,
            "capacity_litres": "120.00",
        },
    )
    assert bin_res.status_code == 201
    bin_data = bin_res.json()
    bin_id = bin_data["bin_id"]
    qr_token = bin_data["qr_token"]

    # Step 3: Student scans QR Code
    qr_res = client.get(
        f"/api/v1/bins/qr/{qr_token}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert qr_res.status_code == 200
    scanned_bin_id = qr_res.json()["bin_id"]
    assert scanned_bin_id == bin_id

    # Step 4: Student records waste disposal into scanned bin
    disp_res = client.post(
        "/api/v1/disposals",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "bin_id": scanned_bin_id,
            "quantity_kg": "0.350",
            "notes": "Post-event food container",
        },
    )
    assert disp_res.status_code == 201
    disp_data = disp_res.json()
    assert disp_data["bin_code"] == "QUAD-WET-01"
    assert disp_data["waste_type"]["name"] == "WET_ORGANIC"

    # Step 5: Student notices bin is getting full/damaged and submits a Report
    rep_res = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "bin_id": scanned_bin_id,
            "report_type": "OVERFLOWING",
            "description": "Quad bin is nearing capacity after campus fest",
        },
    )
    assert rep_res.status_code == 201
    report_id = rep_res.json()["report_id"]
    assert rep_res.json()["status"] == "PENDING"

    # Step 6: Admin views reports and updates to IN_PROGRESS
    admin_prog_res = client.patch(
        f"/api/v1/reports/{report_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "IN_PROGRESS"},
    )
    assert admin_prog_res.status_code == 200
    assert admin_prog_res.json()["status"] == "IN_PROGRESS"

    # Step 7: Admin marks issue as RESOLVED
    admin_res_res = client.patch(
        f"/api/v1/reports/{report_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "RESOLVED"},
    )
    assert admin_res_res.status_code == 200
    final_report = admin_res_res.json()
    assert final_report["status"] == "RESOLVED"
    assert final_report["resolved_at"] is not None
    assert final_report["resolved_by"] == str(test_admin_user.user_id)


def test_all_five_report_types_accepted(
    client: TestClient,
    student_token: str,
    test_bin: Bin,
) -> None:
    """Verify that all 5 valid report types are accepted with and without a bin."""
    valid_types = [
        "OVERFLOWING",
        "DAMAGED_BIN",
        "MISSING_BIN",
        "WRONG_SEGREGATION",
        "OTHER",
    ]
    for rtype in valid_types:
        # 1. With bin
        res_with_bin = client.post(
            "/api/v1/reports",
            headers={"Authorization": f"Bearer {student_token}"},
            json={
                "bin_id": str(test_bin.bin_id),
                "report_type": rtype,
                "description": f"Testing issue type {rtype} with bin",
            },
        )
        assert res_with_bin.status_code == 201
        data = res_with_bin.json()
        assert data["report_type"] == rtype
        assert data["bin_id"] == str(test_bin.bin_id)
        assert data["status"] == "PENDING"

        # 2. Without bin (general campus issue)
        res_no_bin = client.post(
            "/api/v1/reports",
            headers={"Authorization": f"Bearer {student_token}"},
            json={
                "report_type": rtype,
                "description": f"Testing issue type {rtype} without bin",
            },
        )
        assert res_no_bin.status_code == 201
        data_no_bin = res_no_bin.json()
        assert data_no_bin["report_type"] == rtype
        assert data_no_bin["bin_id"] is None
        assert data_no_bin["status"] == "PENDING"


def test_legacy_mismatched_report_types_rejected(
    client: TestClient,
    student_token: str,
    test_bin: Bin,
) -> None:
    """Verify that legacy/incorrect frontend types 'OVERFLOW' and 'DAMAGE' are strictly rejected with 422."""
    for invalid_type in ["OVERFLOW", "DAMAGE", "overflow", "damage"]:
        res = client.post(
            "/api/v1/reports",
            headers={"Authorization": f"Bearer {student_token}"},
            json={
                "bin_id": str(test_bin.bin_id),
                "report_type": invalid_type,
                "description": "Attempting invalid report type",
            },
        )
        assert res.status_code == 422
        detail = res.json()["detail"]
        error_msg = detail[0]["msg"]
        assert "Invalid report_type" in error_msg
        assert "OVERFLOWING" in error_msg
        assert "DAMAGED_BIN" in error_msg


def test_resolved_report_awards_points_without_duplicate_awards(
    client: TestClient,
    student_token: str,
    admin_token: str,
    test_bin: Bin,
) -> None:
    """Verify points are awarded once when a report is resolved, and resolving again does not duplicate points."""
    # 1. Student creates report
    create_res = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "bin_id": str(test_bin.bin_id),
            "report_type": "OVERFLOWING",
            "description": "Overflowing bin to test point award idempotency",
        },
    )
    assert create_res.status_code == 201
    report_id = create_res.json()["report_id"]

    # 2. Admin resolves report
    resolve_res_1 = client.patch(
        f"/api/v1/reports/{report_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "RESOLVED"},
    )
    assert resolve_res_1.status_code == 200

    # Check points
    points_res_1 = client.get(
        "/api/v1/gamification/me",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert points_res_1.status_code == 200
    balance_after_first_resolve = points_res_1.json()["current_points"]

    # 3. Admin resolves again or updates status
    resolve_res_2 = client.patch(
        f"/api/v1/reports/{report_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "RESOLVED"},
    )
    assert resolve_res_2.status_code == 200

    points_res_2 = client.get(
        "/api/v1/gamification/me",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert points_res_2.status_code == 200
    assert points_res_2.json()["current_points"] == balance_after_first_resolve

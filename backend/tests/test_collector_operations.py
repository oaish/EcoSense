import uuid
from datetime import datetime, timezone
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.bin import Bin
from app.models.collection import CollectionRecord
from app.models.location import Location
from app.models.report import WasteReport
from app.models.role import Role
from app.models.user import User
from app.core.security import hash_password, create_access_token


@pytest.fixture
def second_collector(db_session: Session) -> User:
    role = db_session.query(Role).filter(Role.role_name == "COLLECTOR").first()
    user = User(
        name="Second Collector",
        email="collector2@dbit.in",
        password_hash=hash_password("password123"),
        role_id=role.role_id,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def second_collector_token(second_collector: User) -> str:
    return create_access_token(
        subject=str(second_collector.user_id),
        role=second_collector.role.role_name,
    )


# ==============================================================================
# PHASE 1 & 2: ATTENDANCE & AVAILABILITY TESTS
# ==============================================================================

def test_collector_can_check_in(
    client: TestClient,
    collector_token: str,
    test_collector_user: User,
) -> None:
    res = client.post(
        "/api/v1/attendance/check-in",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"notes": "Starting morning campus shift"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["collector_id"] == str(test_collector_user.user_id)
    assert data["status"] == "ACTIVE"
    assert data["check_out_at"] is None
    assert "Starting morning campus shift" in data["notes"]
    assert "attendance_date" in data


def test_collector_can_check_out(
    client: TestClient,
    collector_token: str,
) -> None:
    # 1. Start shift
    in_res = client.post(
        "/api/v1/attendance/check-in",
        headers={"Authorization": f"Bearer {collector_token}"},
    )
    assert in_res.status_code == 201

    # 2. Check active shift endpoint
    me_res = client.get(
        "/api/v1/attendance/me",
        headers={"Authorization": f"Bearer {collector_token}"},
    )
    assert me_res.status_code == 200
    assert me_res.json()["status"] == "ACTIVE"

    # 3. End shift
    out_res = client.post(
        "/api/v1/attendance/check-out",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"notes": "Completed afternoon rounds"},
    )
    assert out_res.status_code == 200
    data = out_res.json()
    assert data["status"] == "COMPLETED"
    assert data["check_out_at"] is not None

    # 4. Verify no active shift remains
    me_res2 = client.get(
        "/api/v1/attendance/me",
        headers={"Authorization": f"Bearer {collector_token}"},
    )
    assert me_res2.status_code == 200
    assert me_res2.json() is None


def test_duplicate_check_in_rejected_409(
    client: TestClient,
    collector_token: str,
) -> None:
    # 1. First check in
    res1 = client.post(
        "/api/v1/attendance/check-in",
        headers={"Authorization": f"Bearer {collector_token}"},
    )
    assert res1.status_code == 201

    # 2. Second check in without closing active shift
    res2 = client.post(
        "/api/v1/attendance/check-in",
        headers={"Authorization": f"Bearer {collector_token}"},
    )
    assert res2.status_code == 409
    assert "Active shift already in progress" in res2.json()["detail"]


def test_check_out_without_active_shift_rejected_400(
    client: TestClient,
    collector_token: str,
) -> None:
    res = client.post(
        "/api/v1/attendance/check-out",
        headers={"Authorization": f"Bearer {collector_token}"},
    )
    assert res.status_code == 400
    assert "No active shift found" in res.json()["detail"]


def test_student_and_staff_cannot_check_in(
    client: TestClient,
    student_token: str,
    staff_token: str,
) -> None:
    res_student = client.post(
        "/api/v1/attendance/check-in",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res_student.status_code == 403

    res_staff = client.post(
        "/api/v1/attendance/check-in",
        headers={"Authorization": f"Bearer {staff_token}"},
    )
    assert res_staff.status_code == 403


def test_collector_attendance_history(
    client: TestClient,
    collector_token: str,
) -> None:
    # Check in & out twice
    client.post("/api/v1/attendance/check-in", headers={"Authorization": f"Bearer {collector_token}"})
    client.post("/api/v1/attendance/check-out", headers={"Authorization": f"Bearer {collector_token}"})
    client.post("/api/v1/attendance/check-in", headers={"Authorization": f"Bearer {collector_token}"})
    client.post("/api/v1/attendance/check-out", headers={"Authorization": f"Bearer {collector_token}"})

    hist_res = client.get(
        "/api/v1/attendance/me/history",
        headers={"Authorization": f"Bearer {collector_token}"},
    )
    assert hist_res.status_code == 200
    items = hist_res.json()
    assert len(items) == 2


def test_admin_can_view_attendance_overview_and_history(
    client: TestClient,
    admin_token: str,
    collector_token: str,
) -> None:
    # Collector checks in
    client.post("/api/v1/attendance/check-in", headers={"Authorization": f"Bearer {collector_token}"})

    # Admin checks overview
    overview_res = client.get(
        "/api/v1/attendance/admin/overview",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert overview_res.status_code == 200
    data = overview_res.json()
    assert data["total_collectors"] >= 1
    assert data["on_shift_collectors"] >= 1
    assert len(data["collectors"]) >= 1

    # Check collector shift summary item
    coll_summary = [c for c in data["collectors"] if c["attendance_status"] == "ON_SHIFT"][0]
    assert coll_summary["check_in_at"] is not None

    # Admin checks history
    hist_res = client.get(
        "/api/v1/attendance/admin/history",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert hist_res.status_code == 200
    assert len(hist_res.json()) >= 1


# ==============================================================================
# PHASE 3, 5 & 6: TASK MANAGEMENT & WORKFLOW TESTS
# ==============================================================================

def test_admin_can_create_and_assign_collection_task(
    client: TestClient,
    admin_token: str,
    test_collector_user: User,
    test_bin: Bin,
) -> None:
    res = client.post(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "task_type": "COLLECTION",
            "collector_id": str(test_collector_user.user_id),
            "bin_id": str(test_bin.bin_id),
            "priority": "HIGH",
            "title": "Empty quad bin after lunch",
            "instructions": "Use heavy duty compostable bag",
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["task_id"] > 0
    assert data["status"] == "ASSIGNED"
    assert data["task_type"] == "COLLECTION"
    assert data["bin_id"] == str(test_bin.bin_id)
    assert data["bin_code"] == test_bin.bin_code
    assert data["collector_id"] == str(test_collector_user.user_id)


def test_non_admin_cannot_create_task(
    client: TestClient,
    collector_token: str,
    test_collector_user: User,
    test_bin: Bin,
) -> None:
    res = client.post(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={
            "task_type": "COLLECTION",
            "collector_id": str(test_collector_user.user_id),
            "bin_id": str(test_bin.bin_id),
            "title": "Unauthorized task",
        },
    )
    assert res.status_code == 403


def test_inactive_or_non_collector_assignment_rejected(
    client: TestClient,
    admin_token: str,
    test_student_user: User,
    test_bin: Bin,
) -> None:
    # Attempt assigning to a student
    res = client.post(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "task_type": "COLLECTION",
            "collector_id": str(test_student_user.user_id),
            "bin_id": str(test_bin.bin_id),
            "title": "Invalid assignment to student",
        },
    )
    assert res.status_code == 400
    assert "does not have the COLLECTOR role" in res.json()["detail"]


def test_collector_can_view_only_own_tasks(
    client: TestClient,
    admin_token: str,
    collector_token: str,
    second_collector_token: str,
    test_collector_user: User,
    second_collector: User,
    test_bin: Bin,
) -> None:
    # 1. Admin assigns task to collector 1
    client.post(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "task_type": "INSPECTION",
            "collector_id": str(test_collector_user.user_id),
            "bin_id": str(test_bin.bin_id),
            "title": "Task for collector 1",
        },
    )

    # 2. Admin assigns task to collector 2
    client.post(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "task_type": "INSPECTION",
            "collector_id": str(second_collector.user_id),
            "bin_id": str(test_bin.bin_id),
            "title": "Task for collector 2",
        },
    )

    # Collector 1 checks tasks
    res1 = client.get(
        "/api/v1/tasks/my",
        headers={"Authorization": f"Bearer {collector_token}"},
    )
    assert res1.status_code == 200
    tasks1 = res1.json()["tasks"]
    assert len(tasks1) == 1
    assert tasks1[0]["title"] == "Task for collector 1"

    # Collector 2 checks tasks
    res2 = client.get(
        "/api/v1/tasks/my",
        headers={"Authorization": f"Bearer {second_collector_token}"},
    )
    assert res2.status_code == 200
    tasks2 = res2.json()["tasks"]
    assert len(tasks2) == 1
    assert tasks2[0]["title"] == "Task for collector 2"


def test_collector_cannot_modify_other_collector_task(
    client: TestClient,
    admin_token: str,
    second_collector_token: str,
    test_collector_user: User,
    test_bin: Bin,
) -> None:
    # Task assigned to collector 1
    create_res = client.post(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "task_type": "INSPECTION",
            "collector_id": str(test_collector_user.user_id),
            "bin_id": str(test_bin.bin_id),
            "title": "Private collector 1 task",
        },
    )
    task_id = create_res.json()["task_id"]

    # Collector 2 attempts to accept it
    mod_res = client.patch(
        f"/api/v1/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {second_collector_token}"},
        json={"status": "ACCEPTED"},
    )
    assert mod_res.status_code == 403


def test_task_status_lifecycle_and_invalid_transitions(
    client: TestClient,
    admin_token: str,
    collector_token: str,
    test_collector_user: User,
    test_bin: Bin,
) -> None:
    # 1. Create task (starts ASSIGNED)
    create_res = client.post(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "task_type": "INSPECTION",
            "collector_id": str(test_collector_user.user_id),
            "bin_id": str(test_bin.bin_id),
            "title": "Inspect bin hinges",
        },
    )
    task_id = create_res.json()["task_id"]

    # 2. Invalid jump: ASSIGNED -> COMPLETED directly should fail
    bad_res = client.patch(
        f"/api/v1/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"status": "COMPLETED", "completion_notes": "Done without starting"},
    )
    assert bad_res.status_code == 400

    # 3. Valid: ASSIGNED -> ACCEPTED
    acc_res = client.patch(
        f"/api/v1/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"status": "ACCEPTED"},
    )
    assert acc_res.status_code == 200
    assert acc_res.json()["status"] == "ACCEPTED"

    # 4. Valid: ACCEPTED -> IN_PROGRESS
    start_res = client.patch(
        f"/api/v1/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"status": "IN_PROGRESS"},
    )
    assert start_res.status_code == 200
    assert start_res.json()["status"] == "IN_PROGRESS"
    assert start_res.json()["started_at"] is not None

    # 5. Valid: IN_PROGRESS -> COMPLETED with notes
    comp_res = client.patch(
        f"/api/v1/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"status": "COMPLETED", "completion_notes": "Inspected, hinges lubricated"},
    )
    assert comp_res.status_code == 200
    assert comp_res.json()["status"] == "COMPLETED"
    assert comp_res.json()["completed_at"] is not None

    # 6. Modifying completed task rejected
    post_comp = client.patch(
        f"/api/v1/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"status": "IN_PROGRESS"},
    )
    assert post_comp.status_code == 400


def test_completing_collection_task_requires_collection_record(
    client: TestClient,
    admin_token: str,
    collector_token: str,
    test_collector_user: User,
    test_bin: Bin,
) -> None:
    # 1. Admin creates COLLECTION task
    create_res = client.post(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "task_type": "COLLECTION",
            "collector_id": str(test_collector_user.user_id),
            "bin_id": str(test_bin.bin_id),
            "title": "Empty quad bin",
        },
    )
    task_id = create_res.json()["task_id"]

    # 2. Collector starts work
    client.patch(
        f"/api/v1/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"status": "IN_PROGRESS"},
    )

    # 3. Attempt completion BEFORE recording a collection record -> rejected
    early_comp = client.patch(
        f"/api/v1/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"status": "COMPLETED"},
    )
    assert early_comp.status_code == 400
    assert "requires a completed waste collection record" in early_comp.json()["detail"]

    # 4. Collector logs collection via existing collection endpoint
    col_res = client.post(
        "/api/v1/collections",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={
            "bin_id": str(test_bin.bin_id),
            "fill_level_before": "85.00",
            "collected_quantity_kg": "12.500",
            "fill_level_after": "0.00",
        },
    )
    assert col_res.status_code == 201
    collection_id = col_res.json()["collection_id"]

    # 5. Now completing task succeeds and links proof of work
    comp_res = client.patch(
        f"/api/v1/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"status": "COMPLETED", "collection_id": collection_id},
    )
    assert comp_res.status_code == 200
    assert comp_res.json()["status"] == "COMPLETED"
    assert comp_res.json()["collection_id"] == collection_id


def test_inspection_task_requires_completion_notes(
    client: TestClient,
    admin_token: str,
    collector_token: str,
    test_collector_user: User,
    test_bin: Bin,
) -> None:
    create_res = client.post(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "task_type": "INSPECTION",
            "collector_id": str(test_collector_user.user_id),
            "bin_id": str(test_bin.bin_id),
            "title": "Check bin integrity",
        },
    )
    task_id = create_res.json()["task_id"]

    client.patch(
        f"/api/v1/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"status": "IN_PROGRESS"},
    )

    # Empty notes rejected
    bad_res = client.patch(
        f"/api/v1/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"status": "COMPLETED"},
    )
    assert bad_res.status_code == 400
    assert "Completion notes are required" in bad_res.json()["detail"]


# ==============================================================================
# PHASE 4: WASTE REPORT DELEGATION TESTS
# ==============================================================================

def test_admin_can_delegate_waste_report_as_issue_response_task(
    client: TestClient,
    student_token: str,
    admin_token: str,
    test_collector_user: User,
    test_bin: Bin,
) -> None:
    # 1. Student submits waste report
    rep_res = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "bin_id": str(test_bin.bin_id),
            "report_type": "OVERFLOWING",
            "description": "Trash spilling out after cultural fest",
        },
    )
    assert rep_res.status_code == 201
    report_id = rep_res.json()["report_id"]

    # 2. Admin delegates report to collector
    del_res = client.post(
        "/api/v1/tasks/delegate-report",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "report_id": report_id,
            "collector_id": str(test_collector_user.user_id),
            "priority": "URGENT",
            "instructions": "Clear overflow before evening classes",
        },
    )
    assert del_res.status_code == 201
    task_data = del_res.json()
    assert task_data["task_type"] == "ISSUE_RESPONSE"
    assert task_data["report_id"] == report_id
    assert task_data["bin_id"] == str(test_bin.bin_id)
    assert task_data["priority"] == "URGENT"
    assert "Overflowing" in task_data["title"]

    # 3. Verify report itself is NOT automatically marked RESOLVED
    check_rep = client.get(
        f"/api/v1/reports/{report_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert check_rep.status_code == 200
    assert check_rep.json()["status"] == "PENDING"


def test_admin_can_reassign_task_with_audit(
    client: TestClient,
    admin_token: str,
    test_collector_user: User,
    second_collector: User,
    test_bin: Bin,
) -> None:
    # 1. Assign to collector 1
    create_res = client.post(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "task_type": "INSPECTION",
            "collector_id": str(test_collector_user.user_id),
            "bin_id": str(test_bin.bin_id),
            "title": "Campus audit",
        },
    )
    task_id = create_res.json()["task_id"]

    # 2. Reassign to collector 2
    reassign_res = client.post(
        f"/api/v1/tasks/{task_id}/reassign",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "new_collector_id": str(second_collector.user_id),
            "instructions": "Reassigned due to shift swap",
            "priority": "HIGH",
        },
    )
    assert reassign_res.status_code == 200
    data = reassign_res.json()
    assert data["collector_id"] == str(second_collector.user_id)
    assert data["collector_name"] == second_collector.name
    assert data["priority"] == "HIGH"
    assert "[Reassigned]" in data["instructions"]


def test_admin_can_cancel_task(
    client: TestClient,
    admin_token: str,
    test_collector_user: User,
    test_bin: Bin,
) -> None:
    create_res = client.post(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "task_type": "INSPECTION",
            "collector_id": str(test_collector_user.user_id),
            "bin_id": str(test_bin.bin_id),
            "title": "Duplicate task to cancel",
        },
    )
    task_id = create_res.json()["task_id"]

    cancel_res = client.post(
        f"/api/v1/tasks/{task_id}/cancel?reason=Created+by+mistake",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"
    assert cancel_res.json()["cancellation_reason"] == "Created by mistake"

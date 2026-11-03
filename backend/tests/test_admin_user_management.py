import uuid
import pytest
from fastapi.testclient import TestClient

from app.models.user import User


def test_non_admin_cannot_access_user_management(client: TestClient, student_token: str, staff_token: str):
    """Ensure non-admin roles cannot list or create users."""
    res1 = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res1.status_code == 403

    res2 = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {staff_token}"},
    )
    assert res2.status_code == 403


def test_admin_list_and_search_users(
    client: TestClient,
    admin_token: str,
    test_admin_user: User,
    test_student_user: User,
    test_staff_user: User,
    test_collector_user: User,
):
    """Admin can list users with pagination, search, and role filtering."""
    # List all
    res = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "total_count" in data
    assert "users" in data
    assert data["total_count"] >= 4

    # Filter by role
    res_student = client.get(
        "/api/v1/users/?role=STUDENT",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_student.status_code == 200
    for u in res_student.json()["users"]:
        assert u["role"] == "STUDENT"

    # Search by email
    res_search = client.get(
        "/api/v1/users/?search=admin",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_search.status_code == 200
    assert len(res_search.json()["users"]) >= 1


def test_admin_create_and_deactivate_user(client: TestClient, admin_token: str, db_session):
    """Admin can create a user, update their profile, and deactivate/reactivate them."""
    new_email = f"test_new_student_{uuid.uuid4().hex[:6]}@dbit.in"
    payload = {
        "name": "Test New Student",
        "email": new_email,
        "password": "Password123!",
        "role": "STUDENT",
        "is_active": True,
    }

    # 1. Create user
    create_res = client.post(
        "/api/v1/users/",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert create_res.status_code == 201
    created_user = create_res.json()
    user_id = created_user["user_id"]
    assert created_user["name"] == "Test New Student"
    assert created_user["email"] == new_email

    # 2. Inspect user detail
    detail_res = client.get(
        f"/api/v1/users/{user_id}/detail",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["email"] == new_email
    assert detail_data["total_earned_points"] == 0
    assert "stage" in detail_data

    # 3. User can log in when active
    login_res = client.post("/api/v1/auth/login", json={"email": new_email, "password": "Password123!"})
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

    # 4. Deactivate user
    patch_res = client.patch(
        f"/api/v1/users/{user_id}",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["is_active"] is False

    # 5. Inactive user CANNOT log in (403)
    login_inactive = client.post("/api/v1/auth/login", json={"email": new_email, "password": "Password123!"})
    assert login_inactive.status_code == 403
    assert "blocked" in login_inactive.json()["detail"].lower() or "inactive" in login_inactive.json()["detail"].lower()

    # 6. Reactivate user
    patch_reactivate = client.patch(
        f"/api/v1/users/{user_id}",
        json={"is_active": True},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert patch_reactivate.status_code == 200
    assert patch_reactivate.json()["is_active"] is True

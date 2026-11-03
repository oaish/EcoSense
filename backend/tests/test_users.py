from fastapi.testclient import TestClient
from app.models.user import User


def test_users_me_endpoint(
    client: TestClient,
    test_student_user: User,
    student_token: str,
) -> None:
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "student@dbit.in"
    assert data["name"] == "Student User"
    assert data["role"] == "STUDENT"
    assert "password_hash" not in data


def test_admin_test_endpoint_with_admin(
    client: TestClient,
    test_admin_user: User,
    admin_token: str,
) -> None:
    response = client.get(
        "/api/v1/users/admin-test",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["admin_user"] == "admin@dbit.in"
    assert "Admin privilege verified" in data["message"]


def test_admin_test_endpoint_with_student(
    client: TestClient,
    test_student_user: User,
    student_token: str,
) -> None:
    response = client.get(
        "/api/v1/users/admin-test",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 403
    assert "Operation not permitted" in response.json()["detail"]


def test_admin_test_endpoint_with_collector(
    client: TestClient,
    test_collector_user: User,
    collector_token: str,
) -> None:
    response = client.get(
        "/api/v1/users/admin-test",
        headers={"Authorization": f"Bearer {collector_token}"},
    )
    assert response.status_code == 403
    assert "Operation not permitted" in response.json()["detail"]


def test_admin_test_endpoint_unauthorized(client: TestClient) -> None:
    response = client.get("/api/v1/users/admin-test")
    assert response.status_code == 401

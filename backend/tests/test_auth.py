from fastapi.testclient import TestClient
from app.models.user import User


def test_login_success(client: TestClient, test_student_user: User) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "student@dbit.in", "password": "studentpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client: TestClient, test_student_user: User) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "student@dbit.in", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_nonexistent_user(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@dbit.in", "password": "anypassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_inactive_user(client: TestClient, test_inactive_user: User) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "inactive@dbit.in", "password": "inactivepass123"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Your account has been blocked. Please contact admin for assistance."


def test_auth_me_without_token(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_auth_me_with_invalid_token(client: TestClient) -> None:
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token_xyz"},
    )
    assert response.status_code == 401


def test_auth_me_with_valid_token(
    client: TestClient,
    test_student_user: User,
    student_token: str,
) -> None:
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "student@dbit.in"
    assert data["name"] == "Student User"
    assert data["role"] == "STUDENT"
    assert data["is_active"] is True
    assert "password_hash" not in data

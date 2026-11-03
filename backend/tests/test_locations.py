from fastapi.testclient import TestClient
from app.models.location import Location


def test_admin_can_create_location(client: TestClient, admin_token: str) -> None:
    response = client.post(
        "/api/v1/locations",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Chemistry Lab",
            "location_type": "LABORATORY",
            "building": "Science Block",
            "floor": "3rd Floor",
            "description": "General chemistry practical lab",
            "latitude": "19.076000",
            "longitude": "72.877700",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Chemistry Lab"
    assert data["location_type"] == "LABORATORY"
    assert data["building"] == "Science Block"
    assert data["floor"] == "3rd Floor"
    assert data["is_active"] is True
    assert "location_id" in data


def test_non_admin_cannot_create_location(client: TestClient, student_token: str) -> None:
    response = client.post(
        "/api/v1/locations",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "name": "Unauthorized Location",
            "location_type": "CLASSROOM",
        },
    )
    assert response.status_code == 403
    assert "Operation not permitted" in response.json()["detail"]


def test_unauthenticated_cannot_create_location(client: TestClient) -> None:
    response = client.post(
        "/api/v1/locations",
        json={"name": "Public Place", "location_type": "OUTDOOR"},
    )
    assert response.status_code == 401


def test_authenticated_user_can_list_locations(
    client: TestClient,
    student_token: str,
    test_location: Location,
) -> None:
    response = client.get(
        "/api/v1/locations",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(loc["location_id"] == test_location.location_id for loc in data)


def test_authenticated_user_can_view_location(
    client: TestClient,
    student_token: str,
    test_location: Location,
) -> None:
    response = client.get(
        f"/api/v1/locations/{test_location.location_id}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["location_id"] == test_location.location_id
    assert data["name"] == test_location.name
    assert data["location_type"] == test_location.location_type


def test_view_nonexistent_location_returns_404(client: TestClient, student_token: str) -> None:
    response = client.get(
        "/api/v1/locations/99999",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_admin_can_update_location(
    client: TestClient,
    admin_token: str,
    test_location: Location,
) -> None:
    response = client.patch(
        f"/api/v1/locations/{test_location.location_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Updated Canteen Name",
            "floor": "Mezzanine Floor",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Canteen Name"
    assert data["floor"] == "Mezzanine Floor"


def test_admin_can_deactivate_location(
    client: TestClient,
    admin_token: str,
    test_location: Location,
) -> None:
    response = client.patch(
        f"/api/v1/locations/{test_location.location_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False


def test_non_admin_cannot_update_location(
    client: TestClient,
    student_token: str,
    test_location: Location,
) -> None:
    response = client.patch(
        f"/api/v1/locations/{test_location.location_id}",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"name": "Hacked Canteen"},
    )
    assert response.status_code == 403

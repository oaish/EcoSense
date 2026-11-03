from fastapi.testclient import TestClient


def test_authenticated_user_can_list_waste_types(client: TestClient, student_token: str) -> None:
    response = client.get(
        "/api/v1/waste-types",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    names = [wt["name"] for wt in data]
    assert "WET_ORGANIC" in names
    assert "DRY_RECYCLABLE" in names
    assert "PAPER" in names
    assert "METAL" in names
    assert "E_WASTE" in names
    assert "GARDEN" in names


def test_unauthenticated_cannot_list_waste_types(client: TestClient) -> None:
    response = client.get("/api/v1/waste-types")
    assert response.status_code == 401


def test_admin_can_create_waste_type(client: TestClient, admin_token: str) -> None:
    response = client.post(
        "/api/v1/waste-types",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "HAZARDOUS",
            "description": "Hazardous lab chemicals and batteries",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "HAZARDOUS"
    assert data["is_active"] is True
    assert "waste_type_id" in data


def test_duplicate_waste_type_name_rejected(client: TestClient, admin_token: str) -> None:
    response = client.post(
        "/api/v1/waste-types",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "WET_ORGANIC",
            "description": "Duplicate wet waste",
        },
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


def test_non_admin_cannot_create_waste_type(client: TestClient, student_token: str) -> None:
    response = client.post(
        "/api/v1/waste-types",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "name": "STUDENT_WASTE",
        },
    )
    assert response.status_code == 403


def test_admin_can_update_waste_type(client: TestClient, admin_token: str) -> None:
    # First get list to find an ID
    list_res = client.get(
        "/api/v1/waste-types",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    wt_id = list_res.json()[0]["waste_type_id"]

    response = client.patch(
        f"/api/v1/waste-types/{wt_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"description": "Updated waste type description"},
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Updated waste type description"

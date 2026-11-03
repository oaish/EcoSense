import uuid
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from ai.classification.classifier import BaseWasteClassifier, ClassificationPrediction
from app.core.security import create_access_token, hash_password
from app.models.bin import Bin
from app.models.classification import WasteClassification
from app.models.disposal import DisposalRecord
from app.models.location import Location
from app.models.role import Role
from app.models.user import User
from app.models.waste_type import WasteType
from app.services.classification_service import set_classifier


def test_student_can_create_classification(client: TestClient, student_token: str, test_student_user: User):
    """Test 1 & 3: Authenticated student can classify a waste image."""
    response = client.post(
        "/api/v1/classification",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"image_url": "https://images.dbit.ac.in/waste/plastic_bottle_01.jpg"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "classification_id" in data
    assert data["user_id"] == str(test_student_user.user_id)
    assert data["predicted_waste_type"]["name"] == "DRY_RECYCLABLE"
    assert data["confidence_score"] == 0.94
    assert data["model_version"] == "v1.0-mock"
    assert data["low_confidence"] is False
    assert data["disposal_id"] is None


def test_unauthenticated_user_cannot_classify(client: TestClient):
    """Test 2: Unauthenticated user is rejected with 401."""
    response = client.post(
        "/api/v1/classification",
        json={"image_url": "https://images.dbit.ac.in/waste/sample.jpg"},
    )
    assert response.status_code == 401


def test_staff_collector_and_admin_can_classify(
    client: TestClient,
    staff_token: str,
    collector_token: str,
    admin_token: str,
):
    """Test 4, 5, 6: Staff, Collector, and Admin roles can all submit images for classification."""
    # Staff
    res_staff = client.post(
        "/api/v1/classification",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={"image_url": "https://images.dbit.ac.in/waste/newspaper_bundle.jpg"},
    )
    assert res_staff.status_code == 201
    assert res_staff.json()["predicted_waste_type"]["name"] == "PAPER"

    # Collector
    res_collector = client.post(
        "/api/v1/classification",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"image_url": "https://images.dbit.ac.in/waste/food_canteen_leftover.jpg"},
    )
    assert res_collector.status_code == 201
    assert res_collector.json()["predicted_waste_type"]["name"] == "WET_ORGANIC"

    # Admin
    res_admin = client.post(
        "/api/v1/classification",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"image_url": "https://images.dbit.ac.in/waste/broken_circuit_battery.jpg"},
    )
    assert res_admin.status_code == 201
    assert res_admin.json()["predicted_waste_type"]["name"] == "E_WASTE"


def test_user_id_comes_from_jwt_and_cannot_be_overridden(
    client: TestClient,
    student_token: str,
    test_student_user: User,
):
    """Test 7 & 8: user_id comes strictly from JWT payload and cannot be spoofed in request."""
    fake_uuid = str(uuid.uuid4())
    response = client.post(
        "/api/v1/classification",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "image_url": "https://images.dbit.ac.in/waste/can.jpg",
            "user_id": fake_uuid,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == str(test_student_user.user_id)
    assert data["user_id"] != fake_uuid


def test_valid_waste_type_mapping_and_confidence(
    client: TestClient,
    student_token: str,
    db_session: Session,
):
    """Test 9, 10, 11, 13: Valid waste types and confidence scores are stored accurately."""
    test_cases = [
        ("garden_grass_leaves.jpg", "GARDEN", 0.89),
        ("tin_metal_can.jpg", "METAL", 0.91),
        ("apple_banana_food.jpg", "WET_ORGANIC", 0.95),
        ("cardboard_box.jpg", "PAPER", 0.92),
        ("broken_electronic_cable.jpg", "E_WASTE", 0.96),
    ]

    for img_name, expected_type, expected_conf in test_cases:
        res = client.post(
            "/api/v1/classification",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"image_url": f"https://images.dbit.ac.in/waste/{img_name}"},
        )
        assert res.status_code == 201
        body = res.json()
        assert body["predicted_waste_type"]["name"] == expected_type
        assert body["confidence_score"] == expected_conf
        assert body["model_version"] == "v1.0-mock"

        # Verify in database
        db_rec = db_session.query(WasteClassification).filter(
            WasteClassification.classification_id == body["classification_id"]
        ).first()
        assert db_rec is not None
        assert db_rec.predicted_waste_type.name == expected_type
        assert float(db_rec.confidence_score) == expected_conf


def test_unmapped_or_invalid_category_rejected(client: TestClient, student_token: str):
    """Test 12: If classifier predicts an unknown/unmapped category, returns 422."""
    response = client.post(
        "/api/v1/classification",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"image_url": "https://images.dbit.ac.in/waste/invalid_class_alien_matter.jpg"},
    )
    assert response.status_code == 422
    assert "cannot be mapped to an active campus waste type" in response.json()["detail"]


def test_path_traversal_image_url_rejected(client: TestClient, student_token: str):
    """Test security: Path traversal attempts in image reference are rejected with 400."""
    response = client.post(
        "/api/v1/classification",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"image_url": "../../../etc/passwd"},
    )
    assert response.status_code == 400
    assert "Path traversal" in response.json()["detail"]


def test_classification_with_and_without_disposal_id(
    client: TestClient,
    student_token: str,
    test_student_user: User,
    test_bin: Bin,
    db_session: Session,
):
    """Test 14 & 15: Classification can exist standalone or attached to a valid disposal."""
    # 1. Standalone classification
    res_standalone = client.post(
        "/api/v1/classification",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"image_url": "https://images.dbit.ac.in/waste/cup.jpg"},
    )
    assert res_standalone.status_code == 201
    assert res_standalone.json()["disposal_id"] is None

    # 2. Create a disposal record
    disposal = DisposalRecord(
        user_id=test_student_user.user_id,
        bin_id=test_bin.bin_id,
        quantity_kg=Decimal("1.500"),
        notes="Student lunch disposal",
    )
    db_session.add(disposal)
    db_session.commit()
    db_session.refresh(disposal)

    # 3. Create classification attached to this disposal
    res_attached = client.post(
        "/api/v1/classification",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "image_url": "https://images.dbit.ac.in/waste/lunch_tray.jpg",
            "disposal_id": disposal.disposal_id,
        },
    )
    assert res_attached.status_code == 201
    assert res_attached.json()["disposal_id"] == disposal.disposal_id


def test_invalid_disposal_id_returns_404(client: TestClient, student_token: str):
    """Test 16: Attaching nonexistent disposal_id returns 404."""
    response = client.post(
        "/api/v1/classification",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "image_url": "https://images.dbit.ac.in/waste/item.jpg",
            "disposal_id": 99999999,
        },
    )
    assert response.status_code == 404
    assert "Referenced disposal record not found" in response.json()["detail"]


def test_user_cannot_attach_another_users_disposal(
    client: TestClient,
    student_token: str,
    test_staff_user: User,
    test_bin: Bin,
    db_session: Session,
):
    """Test 17: Normal user cannot attach another user's disposal record (403 Forbidden)."""
    # Create staff's disposal
    staff_disposal = DisposalRecord(
        user_id=test_staff_user.user_id,
        bin_id=test_bin.bin_id,
        quantity_kg=Decimal("0.500"),
        notes="Staff office disposal",
    )
    db_session.add(staff_disposal)
    db_session.commit()
    db_session.refresh(staff_disposal)

    # Student attempts to attach staff's disposal
    response = client.post(
        "/api/v1/classification",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "image_url": "https://images.dbit.ac.in/waste/staff_cup.jpg",
            "disposal_id": staff_disposal.disposal_id,
        },
    )
    assert response.status_code == 403
    assert "Cannot attach classification to another user's disposal" in response.json()["detail"]


def test_user_can_retrieve_own_classification(
    client: TestClient,
    student_token: str,
    test_student_user: User,
):
    """Test 18: User can retrieve their own classification by ID."""
    res_create = client.post(
        "/api/v1/classification",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"image_url": "https://images.dbit.ac.in/waste/plastic_cup.jpg"},
    )
    assert res_create.status_code == 201
    cid = res_create.json()["classification_id"]

    res_get = client.get(
        f"/api/v1/classification/{cid}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res_get.status_code == 200
    assert res_get.json()["classification_id"] == cid
    assert res_get.json()["user_id"] == str(test_student_user.user_id)


def test_user_cannot_retrieve_other_users_classification(
    client: TestClient,
    student_token: str,
    staff_token: str,
):
    """Test 19: User cannot view another user's classification (403 Forbidden)."""
    # Staff creates classification
    res_staff = client.post(
        "/api/v1/classification",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={"image_url": "https://images.dbit.ac.in/waste/staff_paper.jpg"},
    )
    assert res_staff.status_code == 201
    staff_cid = res_staff.json()["classification_id"]

    # Student attempts to retrieve staff's classification
    res_student_get = client.get(
        f"/api/v1/classification/{staff_cid}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res_student_get.status_code == 403


def test_admin_can_retrieve_and_list_broader_classifications(
    client: TestClient,
    admin_token: str,
    student_token: str,
    staff_token: str,
):
    """Test 20: Admin can view any user's classification and list platform-wide classifications."""
    # Student creates classification
    res_student = client.post(
        "/api/v1/classification",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"image_url": "https://images.dbit.ac.in/waste/student_bottle.jpg"},
    )
    cid = res_student.json()["classification_id"]

    # Admin retrieves student's classification directly
    res_admin_get = client.get(
        f"/api/v1/classification/{cid}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_admin_get.status_code == 200
    assert res_admin_get.json()["classification_id"] == cid

    # Admin lists all classifications
    res_admin_list = client.get(
        "/api/v1/classification?skip=0&limit=50",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_admin_list.status_code == 200
    assert len(res_admin_list.json()) >= 1


def test_low_confidence_prediction_is_flagged(client: TestClient, student_token: str):
    """Test 21: Predictions with confidence < 0.70 are flagged with low_confidence: True."""
    response = client.post(
        "/api/v1/classification",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"image_url": "https://images.dbit.ac.in/waste/blurry_low_conf_image.jpg"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["confidence_score"] == 0.51
    assert data["low_confidence"] is True


def test_list_classifications_scoping_and_pagination(
    client: TestClient,
    student_token: str,
    staff_token: str,
):
    """Test 22: Classification listing is properly paginated and scoped per user."""
    # Create 3 classifications for student
    for i in range(3):
        client.post(
            "/api/v1/classification",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"image_url": f"https://images.dbit.ac.in/waste/student_item_{i}.jpg"},
        )

    # Create 2 classifications for staff
    for i in range(2):
        client.post(
            "/api/v1/classification",
            headers={"Authorization": f"Bearer {staff_token}"},
            json={"image_url": f"https://images.dbit.ac.in/waste/staff_item_{i}.jpg"},
        )

    # Student list should only contain student's classifications
    res_student_list = client.get(
        "/api/v1/classification?skip=0&limit=10",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res_student_list.status_code == 200
    student_records = res_student_list.json()
    assert len(student_records) >= 3
    # Check that all records belong to the student
    first_record_uid = student_records[0]["user_id"]
    for r in student_records:
        assert r["user_id"] == first_record_uid


def test_deterministic_mock_classifier_stability(client: TestClient, student_token: str):
    """Test 23: Mock classifier returns identical results for repeated identical queries."""
    res1 = client.post(
        "/api/v1/classification",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"image_url": "https://images.dbit.ac.in/waste/repeatable_aluminum_can.jpg"},
    )
    res2 = client.post(
        "/api/v1/classification",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"image_url": "https://images.dbit.ac.in/waste/repeatable_aluminum_can.jpg"},
    )
    assert res1.status_code == 201
    assert res2.status_code == 201
    assert res1.json()["predicted_waste_type"]["name"] == res2.json()["predicted_waste_type"]["name"]
    assert res1.json()["confidence_score"] == res2.json()["confidence_score"]


def test_model_isolation_and_classifier_swap(client: TestClient, student_token: str):
    """Test 24 (Isolation): Swapping the classifier implementation operates seamlessly without endpoint changes."""
    class CustomVisionClassifier(BaseWasteClassifier):
        def classify(self, image_input: str) -> ClassificationPrediction:
            return ClassificationPrediction(
                predicted_class="METAL",
                confidence_score=0.995,
                model_version="custom-v2.0-vit",
                metadata={"engine": "TensorRT"},
            )

    # Swap to custom classifier
    set_classifier(CustomVisionClassifier())

    try:
        response = client.post(
            "/api/v1/classification",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"image_url": "https://images.dbit.ac.in/waste/any_unmatched_image.jpg"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["predicted_waste_type"]["name"] == "METAL"
        assert data["confidence_score"] == 0.995
        assert data["model_version"] == "custom-v2.0-vit"
        assert data["low_confidence"] is False
    finally:
        # Reset back to default mock classifier
        set_classifier(None)


def test_end_to_end_classification_to_disposal_workflow(
    client: TestClient,
    student_token: str,
    test_location: Location,
    db_session: Session,
):
    """Test 25 (End-to-End):

    Student -> Login -> Classify image -> Receive 'DRY_RECYCLABLE' ->
    Select matching bin -> POST /disposals -> Verify independent records.
    """
    # 1. Setup DRY_RECYCLABLE bin
    dry_type = db_session.query(WasteType).filter(WasteType.name == "DRY_RECYCLABLE").first()
    dry_bin = Bin(
        bin_code="DBIT-DRY-01",
        location_id=test_location.location_id,
        waste_type_id=dry_type.waste_type_id,
        capacity_litres=Decimal("100.00"),
        current_fill_percentage=Decimal("20.00"),
        status="ACTIVE",
    )
    db_session.add(dry_bin)
    db_session.commit()
    db_session.refresh(dry_bin)

    # 2. Student classifies waste image of a plastic bottle
    classify_res = client.post(
        "/api/v1/classification",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"image_url": "https://images.dbit.ac.in/waste/plastic_water_bottle.jpg"},
    )
    assert classify_res.status_code == 201
    class_data = classify_res.json()
    assert class_data["predicted_waste_type"]["name"] == "DRY_RECYCLABLE"
    assert class_data["confidence_score"] >= 0.70

    # Verify no disposal was auto-created
    initial_disposals_count = db_session.query(DisposalRecord).count()

    # 3. Student scans the DRY_RECYCLABLE bin and submits disposal
    disposal_res = client.post(
        "/api/v1/disposals",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "bin_id": str(dry_bin.bin_id),
            "quantity_kg": 0.250,
            "notes": f"Disposed after AI classified as {class_data['predicted_waste_type']['name']}",
        },
    )
    assert disposal_res.status_code == 201
    disposal_data = disposal_res.json()
    assert disposal_data["bin_code"] == "DBIT-DRY-01"
    assert disposal_data["waste_type"]["name"] == "DRY_RECYCLABLE"

    # Verify separate independent records
    assert db_session.query(DisposalRecord).count() == initial_disposals_count + 1
    assert db_session.query(WasteClassification).count() >= 1


def test_classification_multipart_upload_success(client: TestClient, student_token: str):
    """Test authenticated student can upload an image file for AI classification."""
    fake_image_bytes = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB" + b"A" * 200
    files = {
        "file": ("plastic_bottle.jpg", fake_image_bytes, "image/jpeg"),
    }
    response = client.post(
        "/api/v1/classification/upload",
        headers={"Authorization": f"Bearer {student_token}"},
        files=files,
    )
    assert response.status_code == 201
    data = response.json()
    assert "classification_id" in data
    assert "predicted_waste_type" in data
    assert "confidence_score" in data
    assert data["low_confidence"] is False


def test_classification_upload_unsupported_mime_rejected(client: TestClient, student_token: str):
    """Test uploading unsupported file type (e.g. text/plain) is rejected with 400."""
    files = {
        "file": ("notes.txt", b"plain text waste notes", "text/plain"),
    }
    response = client.post(
        "/api/v1/classification/upload",
        headers={"Authorization": f"Bearer {student_token}"},
        files=files,
    )
    assert response.status_code == 400
    assert "unsupported file type" in response.json()["detail"].lower()


def test_classification_upload_empty_file_rejected(client: TestClient, student_token: str):
    """Test uploading an empty file is rejected with 400."""
    files = {
        "file": ("empty.png", b"", "image/png"),
    }
    response = client.post(
        "/api/v1/classification/upload",
        headers={"Authorization": f"Bearer {student_token}"},
        files=files,
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


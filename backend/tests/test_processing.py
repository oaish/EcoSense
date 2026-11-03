import uuid
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.bin import Bin
from app.models.collection import CollectionRecord
from app.models.fill_reading import BinFillReading
from app.models.location import Location
from app.models.processing import ProcessingRecord
from app.models.user import User
from app.models.waste_type import WasteType


def create_collection_helper(
    db: Session,
    bin_id: uuid.UUID,
    collector_id: uuid.UUID,
    collected_quantity_kg: Decimal | None = Decimal("20.000"),
) -> CollectionRecord:
    collection = CollectionRecord(
        bin_id=bin_id,
        collector_id=collector_id,
        fill_level_before=Decimal("80.00"),
        collected_quantity_kg=collected_quantity_kg,
        fill_level_after=Decimal("0.00"),
        notes="Test collection",
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return collection


def test_admin_can_create_recycling_record(
    client: TestClient,
    admin_token: str,
    db_session: Session,
    test_location: Location,
    test_admin_user: User,
) -> None:
    wt = db_session.query(WasteType).filter(WasteType.name == "DRY_RECYCLABLE").first()
    bin_obj = Bin(
        bin_code="BIN-RECYCLE-01",
        location_id=test_location.location_id,
        waste_type_id=wt.waste_type_id,
        status="ACTIVE",
    )
    db_session.add(bin_obj)
    db_session.commit()
    collection = create_collection_helper(db_session, bin_obj.bin_id, test_admin_user.user_id, Decimal("15.500"))

    response = client.post(
        "/api/v1/processing",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "collection_id": collection.collection_id,
            "processing_type": "RECYCLING",
            "quantity_kg": "15.500",
            "notes": "Sent to campus recycling unit",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["collection_id"] == collection.collection_id
    assert data["processing_type"] == "RECYCLING"
    assert float(data["quantity_kg"]) == 15.500
    assert data["status"] == "COMPLETED"
    assert data["processed_by"] == str(test_admin_user.user_id)
    assert "processing_id" in data
    assert "processed_at" in data


def test_collector_can_create_composting_record(
    client: TestClient,
    collector_token: str,
    db_session: Session,
    test_bin: Bin,
    test_collector_user: User,
) -> None:
    # test_bin is WET_ORGANIC by default in conftest
    collection = create_collection_helper(db_session, test_bin.bin_id, test_collector_user.user_id, Decimal("30.000"))

    response = client.post(
        "/api/v1/processing",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={
            "collection_id": collection.collection_id,
            "processing_type": "COMPOSTING",
            "quantity_kg": "30.000",
            "status": "COMPLETED",
            "notes": "Loaded into bio-composter pit 1",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["collection_id"] == collection.collection_id
    assert data["processing_type"] == "COMPOSTING"
    assert float(data["quantity_kg"]) == 30.000
    assert data["processed_by"] == str(test_collector_user.user_id)


def test_student_cannot_create_processing_record(
    client: TestClient,
    student_token: str,
    db_session: Session,
    test_bin: Bin,
    test_collector_user: User,
) -> None:
    collection = create_collection_helper(db_session, test_bin.bin_id, test_collector_user.user_id)

    response = client.post(
        "/api/v1/processing",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "collection_id": collection.collection_id,
            "processing_type": "COMPOSTING",
            "quantity_kg": "10.000",
        },
    )
    assert response.status_code == 403


def test_staff_cannot_create_processing_record(
    client: TestClient,
    staff_token: str,
    db_session: Session,
    test_bin: Bin,
    test_collector_user: User,
) -> None:
    collection = create_collection_helper(db_session, test_bin.bin_id, test_collector_user.user_id)

    response = client.post(
        "/api/v1/processing",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={
            "collection_id": collection.collection_id,
            "processing_type": "COMPOSTING",
            "quantity_kg": "10.000",
        },
    )
    assert response.status_code == 403


def test_unauthenticated_user_rejected(
    client: TestClient,
    db_session: Session,
    test_bin: Bin,
    test_collector_user: User,
) -> None:
    collection = create_collection_helper(db_session, test_bin.bin_id, test_collector_user.user_id)

    response = client.post(
        "/api/v1/processing",
        json={
            "collection_id": collection.collection_id,
            "processing_type": "COMPOSTING",
            "quantity_kg": "10.000",
        },
    )
    assert response.status_code == 401


def test_nonexistent_collection_returns_404(
    client: TestClient,
    collector_token: str,
) -> None:
    response = client.post(
        "/api/v1/processing",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={
            "collection_id": 999999,
            "processing_type": "COMPOSTING",
            "quantity_kg": "10.000",
        },
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_valid_waste_type_processing_type_combinations(
    client: TestClient,
    admin_token: str,
    db_session: Session,
    test_location: Location,
    test_admin_user: User,
) -> None:
    # Test all specified waste type combinations
    cases = [
        ("WET_ORGANIC", "COMPOSTING"),
        ("GARDEN", "COMPOSTING"),
        ("PAPER", "RECYCLING"),
        ("METAL", "RECYCLING"),
        ("E_WASTE", "RECYCLING"),
        ("DRY_RECYCLABLE", "RECYCLING"),
    ]

    for wt_name, proc_type in cases:
        wt = db_session.query(WasteType).filter(WasteType.name == wt_name).first()
        assert wt is not None, f"Waste type {wt_name} should exist"

        bin_obj = Bin(
            bin_code=f"BIN-{wt_name}-{uuid.uuid4().hex[:6]}",
            location_id=test_location.location_id,
            waste_type_id=wt.waste_type_id,
            status="ACTIVE",
        )
        db_session.add(bin_obj)
        db_session.commit()

        collection = create_collection_helper(db_session, bin_obj.bin_id, test_admin_user.user_id, Decimal("10.000"))

        res = client.post(
            "/api/v1/processing",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "collection_id": collection.collection_id,
                "processing_type": proc_type,
                "quantity_kg": "5.000",
            },
        )
        assert res.status_code == 201, f"Expected 201 for {wt_name} -> {proc_type}, got {res.status_code}: {res.text}"


def test_invalid_waste_type_processing_type_rejected(
    client: TestClient,
    admin_token: str,
    db_session: Session,
    test_location: Location,
    test_admin_user: User,
) -> None:
    # Incompatible pairings
    incompatible = [
        ("WET_ORGANIC", "RECYCLING"),
        ("GARDEN", "RECYCLING"),
        ("PAPER", "COMPOSTING"),
        ("METAL", "COMPOSTING"),
        ("E_WASTE", "COMPOSTING"),
        ("DRY_RECYCLABLE", "COMPOSTING"),
    ]

    for wt_name, proc_type in incompatible:
        wt = db_session.query(WasteType).filter(WasteType.name == wt_name).first()
        bin_obj = Bin(
            bin_code=f"BIN-INCOMPAT-{uuid.uuid4().hex[:6]}",
            location_id=test_location.location_id,
            waste_type_id=wt.waste_type_id,
            status="ACTIVE",
        )
        db_session.add(bin_obj)
        db_session.commit()

        collection = create_collection_helper(db_session, bin_obj.bin_id, test_admin_user.user_id, Decimal("10.000"))

        res = client.post(
            "/api/v1/processing",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "collection_id": collection.collection_id,
                "processing_type": proc_type,
                "quantity_kg": "5.000",
            },
        )
        assert res.status_code == 422, f"Expected 422 for incompatible {wt_name} -> {proc_type}"
        assert "incompatible" in res.json()["detail"].lower()


def test_processing_quantity_must_be_positive(
    client: TestClient,
    collector_token: str,
    db_session: Session,
    test_bin: Bin,
    test_collector_user: User,
) -> None:
    collection = create_collection_helper(db_session, test_bin.bin_id, test_collector_user.user_id)

    # Test 0 and negative quantity
    for qty in ["0", "-5.00", "0.000"]:
        res = client.post(
            "/api/v1/processing",
            headers={"Authorization": f"Bearer {collector_token}"},
            json={
                "collection_id": collection.collection_id,
                "processing_type": "COMPOSTING",
                "quantity_kg": qty,
            },
        )
        assert res.status_code == 422


def test_processing_quantity_cannot_exceed_collected_quantity(
    client: TestClient,
    collector_token: str,
    db_session: Session,
    test_bin: Bin,
    test_collector_user: User,
) -> None:
    # Collection was 20.000 kg
    collection = create_collection_helper(db_session, test_bin.bin_id, test_collector_user.user_id, Decimal("20.000"))

    # Attempt to process 25 kg
    res = client.post(
        "/api/v1/processing",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={
            "collection_id": collection.collection_id,
            "processing_type": "COMPOSTING",
            "quantity_kg": "25.000",
        },
    )
    assert res.status_code == 422
    assert "exceeds" in res.json()["detail"].lower()


def test_multiple_processing_records_partial_consumption_and_cumulative_limit(
    client: TestClient,
    collector_token: str,
    db_session: Session,
    test_bin: Bin,
    test_collector_user: User,
) -> None:
    collection = create_collection_helper(db_session, test_bin.bin_id, test_collector_user.user_id, Decimal("20.000"))

    # Batch 1: Process 12 kg (status: PARTIALLY_PROCESSED)
    res1 = client.post(
        "/api/v1/processing",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={
            "collection_id": collection.collection_id,
            "processing_type": "COMPOSTING",
            "quantity_kg": "12.000",
            "status": "PARTIALLY_PROCESSED",
            "notes": "First partial batch",
        },
    )
    assert res1.status_code == 201
    assert float(res1.json()["quantity_kg"]) == 12.000
    assert res1.json()["status"] == "PARTIALLY_PROCESSED"

    # Batch 2: Try to process 10 kg (12 + 10 = 22 > 20) -> Should fail
    res2 = client.post(
        "/api/v1/processing",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={
            "collection_id": collection.collection_id,
            "processing_type": "COMPOSTING",
            "quantity_kg": "10.000",
        },
    )
    assert res2.status_code == 422
    assert "exceeds" in res2.json()["detail"].lower()

    # Batch 3: Process remaining 8 kg (12 + 8 = 20 <= 20) -> Should succeed
    res3 = client.post(
        "/api/v1/processing",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={
            "collection_id": collection.collection_id,
            "processing_type": "COMPOSTING",
            "quantity_kg": "8.000",
            "status": "COMPLETED",
            "notes": "Second final batch",
        },
    )
    assert res3.status_code == 201
    assert float(res3.json()["quantity_kg"]) == 8.000
    assert res3.json()["status"] == "COMPLETED"


def test_null_collected_quantity_handled_correctly(
    client: TestClient,
    collector_token: str,
    db_session: Session,
    test_bin: Bin,
    test_collector_user: User,
) -> None:
    # Collection has collected_quantity_kg = None
    collection = create_collection_helper(db_session, test_bin.bin_id, test_collector_user.user_id, None)

    res = client.post(
        "/api/v1/processing",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={
            "collection_id": collection.collection_id,
            "processing_type": "COMPOSTING",
            "quantity_kg": "50.000",
            "notes": "Estimated unweighed collection processing",
        },
    )
    assert res.status_code == 201
    assert float(res.json()["quantity_kg"]) == 50.000


def test_processing_record_does_not_modify_collection_or_fill_history(
    client: TestClient,
    collector_token: str,
    db_session: Session,
    test_bin: Bin,
    test_collector_user: User,
) -> None:
    # Add a fill reading
    reading = BinFillReading(
        bin_id=test_bin.bin_id,
        fill_percentage=Decimal("75.00"),
        source="MANUAL",
    )
    db_session.add(reading)
    db_session.commit()

    collection = create_collection_helper(db_session, test_bin.bin_id, test_collector_user.user_id, Decimal("18.000"))
    original_collected_qty = collection.collected_quantity_kg
    original_fill_before = collection.fill_level_before
    original_fill_after = collection.fill_level_after

    # Create processing record
    res = client.post(
        "/api/v1/processing",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={
            "collection_id": collection.collection_id,
            "processing_type": "COMPOSTING",
            "quantity_kg": "18.000",
        },
    )
    assert res.status_code == 201

    # Verify collection record remains completely unchanged
    db_session.expire_all()
    fresh_collection = db_session.get(CollectionRecord, collection.collection_id)
    assert fresh_collection.collected_quantity_kg == original_collected_qty
    assert fresh_collection.fill_level_before == original_fill_before
    assert fresh_collection.fill_level_after == original_fill_after

    # Verify fill reading remains unchanged
    fresh_reading = db_session.get(BinFillReading, reading.reading_id)
    assert fresh_reading.fill_percentage == Decimal("75.00")


def test_processing_history_retrieval_and_filtering(
    client: TestClient,
    collector_token: str,
    admin_token: str,
    staff_token: str,
    student_token: str,
    db_session: Session,
    test_bin: Bin,
    test_collector_user: User,
) -> None:
    collection = create_collection_helper(db_session, test_bin.bin_id, test_collector_user.user_id, Decimal("40.000"))

    # Create 2 records
    r1 = ProcessingRecord(
        collection_id=collection.collection_id,
        processing_type="COMPOSTING",
        quantity_kg=Decimal("15.000"),
        processed_by=test_collector_user.user_id,
        status="PARTIALLY_PROCESSED",
    )
    r2 = ProcessingRecord(
        collection_id=collection.collection_id,
        processing_type="COMPOSTING",
        quantity_kg=Decimal("25.000"),
        processed_by=test_collector_user.user_id,
        status="COMPLETED",
    )
    db_session.add_all([r1, r2])
    db_session.commit()

    # Staff can view
    res_staff = client.get("/api/v1/processing", headers={"Authorization": f"Bearer {staff_token}"})
    assert res_staff.status_code == 200
    assert len(res_staff.json()) >= 2

    # Collector can view
    res_coll = client.get("/api/v1/processing", headers={"Authorization": f"Bearer {collector_token}"})
    assert res_coll.status_code == 200

    # Admin can view
    res_admin = client.get("/api/v1/processing", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200

    # Student cannot view
    res_stud = client.get("/api/v1/processing", headers={"Authorization": f"Bearer {student_token}"})
    assert res_stud.status_code == 403

    # Filter by status
    res_filter_status = client.get(
        "/api/v1/processing?status=PARTIALLY_PROCESSED",
        headers={"Authorization": f"Bearer {staff_token}"},
    )
    assert res_filter_status.status_code == 200
    assert all(item["status"] == "PARTIALLY_PROCESSED" for item in res_filter_status.json())

    # Filter by collection_id
    res_filter_col = client.get(
        f"/api/v1/processing?collection_id={collection.collection_id}",
        headers={"Authorization": f"Bearer {staff_token}"},
    )
    assert res_filter_col.status_code == 200
    assert len(res_filter_col.json()) == 2


def test_collection_specific_processing_history(
    client: TestClient,
    staff_token: str,
    db_session: Session,
    test_bin: Bin,
    test_collector_user: User,
) -> None:
    collection = create_collection_helper(db_session, test_bin.bin_id, test_collector_user.user_id, Decimal("15.000"))

    p = ProcessingRecord(
        collection_id=collection.collection_id,
        processing_type="COMPOSTING",
        quantity_kg=Decimal("15.000"),
        processed_by=test_collector_user.user_id,
        status="COMPLETED",
    )
    db_session.add(p)
    db_session.commit()

    res = client.get(
        f"/api/v1/collections/{collection.collection_id}/processing",
        headers={"Authorization": f"Bearer {staff_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["collection_id"] == collection.collection_id
    assert float(data[0]["quantity_kg"]) == 15.000


def test_bin_specific_processing_history(
    client: TestClient,
    staff_token: str,
    db_session: Session,
    test_bin: Bin,
    test_collector_user: User,
) -> None:
    collection = create_collection_helper(db_session, test_bin.bin_id, test_collector_user.user_id, Decimal("22.000"))

    p = ProcessingRecord(
        collection_id=collection.collection_id,
        processing_type="COMPOSTING",
        quantity_kg=Decimal("22.000"),
        processed_by=test_collector_user.user_id,
        status="COMPLETED",
    )
    db_session.add(p)
    db_session.commit()

    res = client.get(
        f"/api/v1/bins/{test_bin.bin_id}/processing",
        headers={"Authorization": f"Bearer {staff_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["collection_id"] == collection.collection_id
    assert float(data[0]["quantity_kg"]) == 22.000


def test_get_single_processing_record_by_id(
    client: TestClient,
    staff_token: str,
    db_session: Session,
    test_bin: Bin,
    test_collector_user: User,
) -> None:
    collection = create_collection_helper(db_session, test_bin.bin_id, test_collector_user.user_id, Decimal("10.000"))

    p = ProcessingRecord(
        collection_id=collection.collection_id,
        processing_type="COMPOSTING",
        quantity_kg=Decimal("10.000"),
        processed_by=test_collector_user.user_id,
        status="COMPLETED",
        notes="Unique note for single lookup",
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    res = client.get(
        f"/api/v1/processing/{p.processing_id}",
        headers={"Authorization": f"Bearer {staff_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["processing_id"] == p.processing_id
    assert data["notes"] == "Unique note for single lookup"

    # Nonexistent ID returns 404
    res_404 = client.get(
        "/api/v1/processing/999999",
        headers={"Authorization": f"Bearer {staff_token}"},
    )
    assert res_404.status_code == 404


def test_end_to_end_collection_to_processing_workflow(
    client: TestClient,
    admin_token: str,
    collector_token: str,
    staff_token: str,
) -> None:
    # 1. Admin creates a new location
    loc_res = client.post(
        "/api/v1/locations",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "DBIT Compost Yard",
            "location_type": "OUTDOOR",
            "building": "Campus Grounds",
            "floor": "Ground",
        },
    )
    assert loc_res.status_code == 201
    location_id = loc_res.json()["location_id"]

    # 2. Get GARDEN waste type
    wt_res = client.get("/api/v1/waste-types", headers={"Authorization": f"Bearer {admin_token}"})
    assert wt_res.status_code == 200
    garden_wt = next(wt for wt in wt_res.json() if wt["name"] == "GARDEN")

    # 3. Admin creates a bin for garden waste
    bin_res = client.post(
        "/api/v1/bins",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "bin_code": "GARDEN-YARD-01",
            "location_id": location_id,
            "waste_type_id": garden_wt["waste_type_id"],
            "capacity_litres": "120.00",
        },
    )
    assert bin_res.status_code == 201
    bin_id = bin_res.json()["bin_id"]

    # 4. Collector records a waste collection of 35.5 kg
    col_res = client.post(
        "/api/v1/collections",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={
            "bin_id": bin_id,
            "fill_level_before": "90.00",
            "collected_quantity_kg": "35.500",
            "fill_level_after": "0.00",
            "notes": "Morning yard clearing collection",
        },
    )
    assert col_res.status_code == 201
    collection_id = col_res.json()["collection_id"]

    # 5. Collector records processing of the collection into COMPOSTING
    proc_res = client.post(
        "/api/v1/processing",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={
            "collection_id": collection_id,
            "processing_type": "COMPOSTING",
            "quantity_kg": "35.500",
            "status": "COMPLETED",
            "notes": "Processed into yard shredder and compost pile #2",
        },
    )
    assert proc_res.status_code == 201
    processing_id = proc_res.json()["processing_id"]

    # 6. Staff views processing history for the collection
    staff_col_proc = client.get(
        f"/api/v1/collections/{collection_id}/processing",
        headers={"Authorization": f"Bearer {staff_token}"},
    )
    assert staff_col_proc.status_code == 200
    assert len(staff_col_proc.json()) == 1
    assert staff_col_proc.json()[0]["processing_id"] == processing_id

    # 7. Staff views processing history for the bin
    staff_bin_proc = client.get(
        f"/api/v1/bins/{bin_id}/processing",
        headers={"Authorization": f"Bearer {staff_token}"},
    )
    assert staff_bin_proc.status_code == 200
    assert len(staff_bin_proc.json()) == 1
    assert staff_bin_proc.json()[0]["processing_id"] == processing_id

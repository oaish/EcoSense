import uuid
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.bin import Bin
from app.models.disposal import DisposalRecord
from app.models.gamification import PointRule, PointTransaction, Reward, RewardRedemption
from app.models.location import Location
from app.models.report import WasteReport
from app.models.user import User
from app.models.waste_type import WasteType
from app.services.gamification_service import (
    award_points_for_disposal,
    award_points_for_report,
    get_user_point_balance,
)


def test_student_starts_with_zero_points(
    client: TestClient,
    student_token: str,
    test_student_user: User,
) -> None:
    res = client.get("/api/v1/gamification/me", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["user_id"] == str(test_student_user.user_id)
    assert data["current_points"] == 0
    assert data["total_earned"] == 0
    assert data["total_redeemed"] == 0


def test_disposal_earns_configured_points_and_anti_duplication(
    client: TestClient,
    student_token: str,
    test_bin: Bin,
    test_student_user: User,
    db_session: Session,
) -> None:
    # Student submits a digital disposal
    res = client.post(
        "/api/v1/disposals",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "bin_id": str(test_bin.bin_id),
            "quantity_kg": "1.500",
            "notes": "Plastic bottle recycling",
        },
    )
    assert res.status_code == 201
    disposal_id = res.json()["disposal_id"]

    # Check student balance (should be 10 points)
    bal_res = client.get("/api/v1/gamification/me", headers={"Authorization": f"Bearer {student_token}"})
    assert bal_res.status_code == 200
    assert bal_res.json()["current_points"] == 10
    assert bal_res.json()["total_earned"] == 10

    # Verify transaction in ledger
    txn_res = client.get("/api/v1/gamification/me/transactions", headers={"Authorization": f"Bearer {student_token}"})
    assert txn_res.status_code == 200
    txns = txn_res.json()
    assert len(txns) == 1
    assert txns[0]["transaction_type"] == "EARN"
    assert txns[0]["points"] == 10
    assert txns[0]["source_type"] == "DISPOSAL"
    assert txns[0]["source_id"] == disposal_id

    # Anti-duplication: Attempting to call award_points_for_disposal directly again
    disposal_obj = db_session.get(DisposalRecord, disposal_id)
    repeat_txn = award_points_for_disposal(db_session, test_student_user, disposal_obj)
    db_session.commit()
    assert repeat_txn.transaction_id == txns[0]["transaction_id"]

    # Balance remains 10
    bal_after = client.get("/api/v1/gamification/me", headers={"Authorization": f"Bearer {student_token}"})
    assert bal_after.json()["current_points"] == 10


def test_report_earns_points_only_when_resolved(
    client: TestClient,
    student_token: str,
    admin_token: str,
    test_bin: Bin,
    test_student_user: User,
    db_session: Session,
) -> None:
    # 1. Student creates a report (status = PENDING)
    rep_res = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "bin_id": str(test_bin.bin_id),
            "report_type": "OVERFLOWING",
            "description": "Bin is overflowing near canteen entrance",
        },
    )
    assert rep_res.status_code == 201
    report_id = rep_res.json()["report_id"]

    # Balance should still be 0 (or unchanged)
    bal_pending = get_user_point_balance(db_session, test_student_user.user_id)
    initial_points = bal_pending["current_points"]

    # 2. Admin updates report to IN_PROGRESS -> Still no points
    client.patch(
        f"/api/v1/reports/{report_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "IN_PROGRESS"},
    )
    bal_in_progress = get_user_point_balance(db_session, test_student_user.user_id)
    assert bal_in_progress["current_points"] == initial_points

    # 3. Admin updates report to RESOLVED -> Awards 5 points
    res_resolved = client.patch(
        f"/api/v1/reports/{report_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "RESOLVED"},
    )
    assert res_resolved.status_code == 200

    bal_resolved = get_user_point_balance(db_session, test_student_user.user_id)
    assert bal_resolved["current_points"] == initial_points + 5
    assert bal_resolved["total_earned"] == initial_points + 5

    # 4. Repeat update does not award duplicate points
    client.patch(
        f"/api/v1/reports/{report_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"description": "Updated notes on resolution"},
    )
    bal_repeat = get_user_point_balance(db_session, test_student_user.user_id)
    assert bal_repeat["current_points"] == initial_points + 5


def test_rejected_report_does_not_earn_points(
    client: TestClient,
    student_token: str,
    admin_token: str,
    test_student_user: User,
    db_session: Session,
) -> None:
    initial_points = get_user_point_balance(db_session, test_student_user.user_id)["current_points"]

    rep_res = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "report_type": "OTHER",
            "description": "False report",
        },
    )
    assert rep_res.status_code == 201
    report_id = rep_res.json()["report_id"]

    # Admin rejects report
    client.patch(
        f"/api/v1/reports/{report_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "REJECTED"},
    )

    bal = get_user_point_balance(db_session, test_student_user.user_id)
    assert bal["current_points"] == initial_points


def test_admin_point_adjustment_and_balance_aggregation(
    client: TestClient,
    admin_token: str,
    test_student_user: User,
    db_session: Session,
) -> None:
    initial_points = get_user_point_balance(db_session, test_student_user.user_id)["current_points"]

    # Admin awards bonus 50 points
    res_bonus = client.post(
        f"/api/v1/gamification/users/{test_student_user.user_id}/adjust",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "points": 50,
            "reason": "Campus clean-up drive participation bonus",
        },
    )
    assert res_bonus.status_code == 201
    data_bonus = res_bonus.json()
    assert data_bonus["points"] == 50
    assert data_bonus["transaction_type"] == "ADJUSTMENT"
    assert data_bonus["source_type"] == "ADMIN_ADJUSTMENT"

    # Admin deducts 15 points
    res_deduct = client.post(
        f"/api/v1/gamification/users/{test_student_user.user_id}/adjust",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "points": -15,
            "reason": "Correction of accidental double entry",
        },
    )
    assert res_deduct.status_code == 201

    # Check updated balance
    bal = client.get(
        f"/api/v1/gamification/users/{test_student_user.user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert bal.status_code == 200
    assert bal.json()["current_points"] == initial_points + 50 - 15


def test_gamification_rbac(
    client: TestClient,
    student_token: str,
    staff_token: str,
    collector_token: str,
    admin_token: str,
    test_student_user: User,
) -> None:
    # 1. Student cannot inspect another user's balance
    fake_uuid = uuid.uuid4()
    res_stud_view_other = client.get(
        f"/api/v1/gamification/users/{fake_uuid}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res_stud_view_other.status_code == 403

    # 2. Student cannot adjust points
    res_stud_adj = client.post(
        f"/api/v1/gamification/users/{test_student_user.user_id}/adjust",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"points": 100, "reason": "Self-award"},
    )
    assert res_stud_adj.status_code == 403

    # 3. Staff cannot adjust points
    res_staff_adj = client.post(
        f"/api/v1/gamification/users/{test_student_user.user_id}/adjust",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={"points": 100, "reason": "Staff attempt"},
    )
    assert res_staff_adj.status_code == 403

    # 4. Collector cannot adjust points
    res_coll_adj = client.post(
        f"/api/v1/gamification/users/{test_student_user.user_id}/adjust",
        headers={"Authorization": f"Bearer {collector_token}"},
        json={"points": 100, "reason": "Collector attempt"},
    )
    assert res_coll_adj.status_code == 403

    # 5. Non-admin cannot create rewards
    res_stud_create_reward = client.post(
        "/api/v1/rewards",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"name": "Fake Reward", "points_cost": 50},
    )
    assert res_stud_create_reward.status_code == 403


def test_reward_creation_listing_and_admin_updates(
    client: TestClient,
    admin_token: str,
    student_token: str,
) -> None:
    # Admin creates active reward
    res_create = client.post(
        "/api/v1/rewards",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Eco-Friendly Bamboo Pen",
            "description": "Sustainable DBIT branded bamboo ballpoint pen",
            "points_cost": 30,
            "stock_quantity": 10,
            "is_active": True,
        },
    )
    assert res_create.status_code == 201
    reward_id = res_create.json()["reward_id"]

    # Student lists rewards (active reward is visible)
    res_list = client.get("/api/v1/rewards", headers={"Authorization": f"Bearer {student_token}"})
    assert res_list.status_code == 200
    assert any(r["reward_id"] == reward_id for r in res_list.json())

    # Admin updates points_cost from 30 to 100
    res_update_cost = client.patch(
        f"/api/v1/rewards/{reward_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"points_cost": 100, "is_active": True},
    )
    assert res_update_cost.status_code == 200
    assert res_update_cost.json()["points_cost"] == 100

    # Verify GET returns updated points_cost
    res_get = client.get(f"/api/v1/rewards/{reward_id}", headers={"Authorization": f"Bearer {student_token}"})
    assert res_get.status_code == 200
    assert res_get.json()["points_cost"] == 100

    # Admin deactivates reward
    res_deactivate = client.patch(
        f"/api/v1/rewards/{reward_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False},
    )
    assert res_deactivate.status_code == 200
    assert res_deactivate.json()["is_active"] is False

    # Student no longer sees inactive reward in list
    res_list_after = client.get("/api/v1/rewards", headers={"Authorization": f"Bearer {student_token}"})
    assert not any(r["reward_id"] == reward_id for r in res_list_after.json())

    # Admin still sees inactive reward
    res_admin_list = client.get("/api/v1/rewards", headers={"Authorization": f"Bearer {admin_token}"})
    assert any(r["reward_id"] == reward_id for r in res_admin_list.json())


def test_reward_redemption_workflow(
    client: TestClient,
    admin_token: str,
    student_token: str,
    test_student_user: User,
) -> None:
    # 1. Admin creates a test reward costing 40 points (finite stock = 2)
    res_reward = client.post(
        "/api/v1/rewards",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Organic DBIT Tote Bag",
            "points_cost": 40,
            "stock_quantity": 2,
            "is_active": True,
        },
    )
    reward_id = res_reward.json()["reward_id"]

    # 2. Student tries to redeem with 0/insufficient points -> 422
    res_fail = client.post(
        f"/api/v1/rewards/{reward_id}/redeem",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res_fail.status_code == 422
    assert "insufficient" in res_fail.json()["detail"].lower()

    # 3. Admin gives student 100 points
    client.post(
        f"/api/v1/gamification/users/{test_student_user.user_id}/adjust",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"points": 100, "reason": "Redemption testing grant"},
    )

    # 4. Student redeems reward #1 (Stock: 2 -> 1, Points: 100 -> 60)
    res_redeem1 = client.post(
        f"/api/v1/rewards/{reward_id}/redeem",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res_redeem1.status_code == 201
    data1 = res_redeem1.json()
    assert data1["points_spent"] == 40
    assert data1["remaining_points"] == 60
    assert data1["status"] == "PENDING"
    assert data1["reward_name"] == "Organic DBIT Tote Bag"

    # 5. Student redeems reward #2 (Stock: 1 -> 0, Points: 60 -> 20)
    res_redeem2 = client.post(
        f"/api/v1/rewards/{reward_id}/redeem",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res_redeem2.status_code == 201
    assert res_redeem2.json()["remaining_points"] == 20

    # 6. Student attempts redemption #3 (Out of Stock) -> 422
    res_out_of_stock = client.post(
        f"/api/v1/rewards/{reward_id}/redeem",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res_out_of_stock.status_code == 422
    assert "out of stock" in res_out_of_stock.json()["detail"].lower()

    # 7. Verify redemption history
    res_my_redemptions = client.get(
        "/api/v1/gamification/me/redemptions",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res_my_redemptions.status_code == 200
    assert len(res_my_redemptions.json()) >= 2


def test_inactive_reward_cannot_be_redeemed(
    client: TestClient,
    admin_token: str,
    student_token: str,
    test_student_user: User,
) -> None:
    # Grant student points
    client.post(
        f"/api/v1/gamification/users/{test_student_user.user_id}/adjust",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"points": 200, "reason": "Points grant"},
    )

    # Admin creates inactive reward
    res_reward = client.post(
        "/api/v1/rewards",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Discontinued Campus Mug",
            "points_cost": 25,
            "is_active": False,
        },
    )
    reward_id = res_reward.json()["reward_id"]

    # Student attempts redemption -> 422
    res_redeem = client.post(
        f"/api/v1/rewards/{reward_id}/redeem",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res_redeem.status_code == 422
    assert "inactive" in res_redeem.json()["detail"].lower()


def test_adjustment_validation(
    client: TestClient,
    admin_token: str,
    test_student_user: User,
) -> None:
    # Zero points rejected
    res_zero = client.post(
        f"/api/v1/gamification/users/{test_student_user.user_id}/adjust",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"points": 0, "reason": "Zero test"},
    )
    assert res_zero.status_code == 422

    # Empty reason rejected
    res_empty_reason = client.post(
        f"/api/v1/gamification/users/{test_student_user.user_id}/adjust",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"points": 10, "reason": "   "},
    )
    assert res_empty_reason.status_code == 422


def test_full_gamification_lifecycle_scenario(
    client: TestClient,
    admin_token: str,
    student_token: str,
    test_location: Location,
    db_session: Session,
) -> None:
    # 1. Setup new clean bin
    wt = db_session.query(WasteType).filter(WasteType.name == "DRY_RECYCLABLE").first()
    bin_obj = Bin(
        bin_code="BIN-GAME-E2E-01",
        location_id=test_location.location_id,
        waste_type_id=wt.waste_type_id,
        status="ACTIVE",
    )
    db_session.add(bin_obj)
    db_session.commit()

    # 2. Student performs 2 disposals (10 pts + 10 pts = 20 pts)
    for _ in range(2):
        d_res = client.post(
            "/api/v1/disposals",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"bin_id": str(bin_obj.bin_id)},
        )
        assert d_res.status_code == 201

    # 3. Student submits an issue report and admin resolves it (+5 pts)
    rep_res = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "bin_id": str(bin_obj.bin_id),
            "report_type": "WRONG_SEGREGATION",
            "description": "Contamination in recyclable bin",
        },
    )
    assert rep_res.status_code == 201
    report_id = rep_res.json()["report_id"]

    res_resolve = client.patch(
        f"/api/v1/reports/{report_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "RESOLVED"},
    )
    assert res_resolve.status_code == 200

    # 4. Check student balance (should have earned 25 points from these 3 activities)
    bal_res = client.get("/api/v1/gamification/me", headers={"Authorization": f"Bearer {student_token}"})
    assert bal_res.status_code == 200
    assert bal_res.json()["current_points"] >= 25

    # 5. Admin creates a badge reward for 25 points
    rew_res = client.post(
        "/api/v1/rewards",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "EcoSense Zero Waste Champion Badge",
            "points_cost": 25,
            "is_active": True,
        },
    )
    assert rew_res.status_code == 201
    reward_id = rew_res.json()["reward_id"]

    # 6. Student redeems the badge
    red_res = client.post(
        f"/api/v1/rewards/{reward_id}/redeem",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert red_res.status_code == 201
    assert red_res.json()["points_spent"] == 25

    # 7. Verify ledger contains all transactions (2 EARN from DISPOSAL, 1 EARN from REPORT, 1 REDEEM from REWARD_REDEMPTION)
    txns_res = client.get(
        "/api/v1/gamification/me/transactions",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert txns_res.status_code == 200
    txns = txns_res.json()
    source_types = [t["source_type"] for t in txns]
    assert "DISPOSAL" in source_types
    assert "REPORT" in source_types
    assert "REWARD_REDEMPTION" in source_types

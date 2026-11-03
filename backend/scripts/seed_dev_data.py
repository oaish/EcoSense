import os
import sys
from decimal import Decimal

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.bin import Bin
from app.models.location import Location
from app.models.waste_type import WasteType
from app.services.auth_service import create_user, get_user_by_email
from app.services.bin_service import create_bin, get_bin_by_code
from app.services.location_service import create_location
from app.services.waste_type_service import create_waste_type, get_waste_type_by_name
from app.schemas.bin import BinCreate
from app.schemas.location import LocationCreate
from app.schemas.waste_type import WasteTypeCreate


def seed_development_data() -> None:
    db = SessionLocal()
    try:
        print("=== 1. Seeding Development Users ===")
        users_to_seed = [
            (
                "System Admin",
                settings.DEV_ADMIN_EMAIL,
                settings.DEV_ADMIN_PASSWORD,
                "ADMIN",
            ),
            (
                "Campus Student",
                settings.DEV_STUDENT_EMAIL,
                settings.DEV_STUDENT_PASSWORD,
                "STUDENT",
            ),
            (
                "Waste Collector",
                settings.DEV_COLLECTOR_EMAIL,
                settings.DEV_COLLECTOR_PASSWORD,
                "COLLECTOR",
            ),
            (
                "Department Staff",
                settings.DEV_STAFF_EMAIL,
                settings.DEV_STAFF_PASSWORD,
                "STAFF",
            ),
        ]

        for name, email, password, role in users_to_seed:
            existing = get_user_by_email(db, email)
            if existing:
                print(f"[EXISTS] User: {email} ({existing.role.role_name})")
            else:
                user = create_user(
                    db=db,
                    name=name,
                    email=email,
                    password=password,
                    role_name=role,
                )
                print(f"[CREATED] User: {user.email} (Role: {role}, ID: {user.user_id})")

        print("\n=== 2. Seeding Waste Types ===")
        initial_waste_types = [
            ("WET_ORGANIC", "Organic and food waste suitable for composting"),
            ("DRY_RECYCLABLE", "Clean plastics, metals, and dry recyclable items"),
            ("PAPER", "Paper and cardboard waste"),
            ("METAL", "Scrap metals, cans, and foil"),
            ("E_WASTE", "Electronic equipment and circuit components"),
            ("GARDEN", "Landscaping and garden trimming waste"),
        ]

        waste_type_map = {}
        for wt_name, desc in initial_waste_types:
            wt = get_waste_type_by_name(db, wt_name)
            if wt:
                print(f"[EXISTS] Waste Type: {wt_name} (ID: {wt.waste_type_id})")
                waste_type_map[wt_name] = wt
            else:
                wt = create_waste_type(db, WasteTypeCreate(name=wt_name, description=desc))
                print(f"[CREATED] Waste Type: {wt_name} (ID: {wt.waste_type_id})")
                waste_type_map[wt_name] = wt

        print("\n=== 3. Seeding Sample Campus Locations ===")
        sample_locations = [
            ("Canteen", "CANTEEN", "Main Building", "Ground Floor", "Main dining and food preparation area"),
            ("Computer Lab", "LABORATORY", "Engineering Block", "2nd Floor", "Computer and IT department laboratory"),
            ("Admin Office", "ADMINISTRATIVE", "Admin Block", "1st Floor", "Central administrative offices"),
            ("Workshop", "WORKSHOP", "Mechanical Shed", "Ground Floor", "Mechanical engineering and fabrication workshop"),
            ("Campus Garden", "OUTDOOR", "Campus Grounds", "Ground Floor", "Central campus lawn and botanical garden"),
        ]

        location_map = {}
        for loc_name, ltype, bldg, flr, desc in sample_locations:
            loc = db.query(Location).filter(Location.name == loc_name).first()
            if loc:
                print(f"[EXISTS] Location: {loc_name} (ID: {loc.location_id})")
                location_map[loc_name] = loc
            else:
                loc = create_location(
                    db,
                    LocationCreate(
                        name=loc_name,
                        location_type=ltype,
                        building=bldg,
                        floor=flr,
                        description=desc,
                    ),
                )
                print(f"[CREATED] Location: {loc_name} (ID: {loc.location_id})")
                location_map[loc_name] = loc

        print("\n=== 4. Seeding Sample Campus Bins ===")
        sample_bins = [
            ("B-001", "Canteen", "WET_ORGANIC", Decimal("50.00")),
            ("B-002", "Canteen", "DRY_RECYCLABLE", Decimal("50.00")),
            ("B-003", "Admin Office", "PAPER", Decimal("30.00")),
            ("B-004", "Computer Lab", "E_WASTE", Decimal("40.00")),
            ("B-005", "Campus Garden", "GARDEN", Decimal("100.00")),
        ]

        for bcode, loc_name, wt_name, cap in sample_bins:
            existing_bin = get_bin_by_code(db, bcode)
            if existing_bin:
                print(f"[EXISTS] Bin: {bcode} -> {loc_name} -> {wt_name} (QR Token: {existing_bin.qr_token})")
            else:
                loc = location_map[loc_name]
                wt = waste_type_map[wt_name]
                new_bin = create_bin(
                    db,
                    BinCreate(
                        bin_code=bcode,
                        location_id=loc.location_id,
                        waste_type_id=wt.waste_type_id,
                        capacity_litres=cap,
                    ),
                )
                print(f"[CREATED] Bin: {new_bin.bin_code} -> {loc_name} -> {wt_name} (QR Token: {new_bin.qr_token})")

        print("\n=== 5. Seeding Sample Campus Rewards ===")
        from app.models.gamification import Reward
        sample_rewards = [
            ("Campus Canteen Meal Voucher", "Enjoy a free meal voucher worth ₹100 at the DBIT campus canteen.", 150, 50),
            ("Eco-Friendly Bamboo Water Bottle", "Insulated, reusable bamboo water bottle with DBIT EcoSense branding.", 300, 25),
            ("Recycled Paper Notebook & Pen", "100% post-consumer recycled notebook and seed-plantable pen.", 100, 100),
            ("DBIT Eco-Warrior Cotton Tote Bag", "Durable organic cotton tote bag for carrying books and groceries.", 200, 40),
            ("Plant-a-Tree Campus Dedication", "Sponsor a sapling planted on campus with a dedication plaque in your name.", 500, 15),
        ]

        for rname, rdesc, rcost, rstock in sample_rewards:
            existing_reward = db.query(Reward).filter(Reward.name == rname).first()
            if existing_reward:
                print(f"[EXISTS] Reward: {rname} (Cost: {existing_reward.points_cost} pts)")
            else:
                new_reward = Reward(
                    name=rname,
                    description=rdesc,
                    points_cost=rcost,
                    stock_quantity=rstock,
                    is_active=True,
                )
                db.add(new_reward)
                db.commit()
                db.refresh(new_reward)
                print(f"[CREATED] Reward: {new_reward.name} (Cost: {new_reward.points_cost} pts, ID: {new_reward.reward_id})")

        print("\n=== Seeding Finished Successfully ===")
    finally:
        db.close()


if __name__ == "__main__":
    seed_development_data()

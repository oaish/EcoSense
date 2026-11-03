from decimal import Decimal
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.base import Base
from app.models.bin import Bin
from app.models.gamification import PointRule
from app.models.location import Location
from app.models.role import Role
from app.models.user import User
from app.models.waste_type import WasteType

# In-memory SQLite for high-speed, isolated unit and integration tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=engine)
    with TestingSessionLocal() as session:
        # Seed initial roles
        roles = [
            Role(role_name="STUDENT"),
            Role(role_name="STAFF"),
            Role(role_name="COLLECTOR"),
            Role(role_name="ADMIN"),
        ]
        session.add_all(roles)

        # Seed initial 6 waste types
        waste_types = [
            WasteType(name="WET_ORGANIC", description="Organic and food waste", is_active=True),
            WasteType(name="DRY_RECYCLABLE", description="Dry recyclable waste", is_active=True),
            WasteType(name="PAPER", description="Paper waste", is_active=True),
            WasteType(name="METAL", description="Metal waste", is_active=True),
            WasteType(name="E_WASTE", description="Electronic waste", is_active=True),
            WasteType(name="GARDEN", description="Garden and landscaping waste", is_active=True),
        ]
        session.add_all(waste_types)

        # Seed initial point rules
        point_rules = [
            PointRule(action_type="DISPOSAL", points=10, description="Points awarded for waste disposal", is_active=True),
            PointRule(action_type="WASTE_REPORT", points=5, description="Points awarded for verified waste report", is_active=True),
        ]
        session.add_all(point_rules)

        session.commit()
    yield
    Base.metadata.drop_all(bind=engine)



@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_admin_user(db_session: Session) -> User:
    role = db_session.query(Role).filter(Role.role_name == "ADMIN").first()
    user = User(
        name="Admin User",
        email="admin@dbit.in",
        password_hash=hash_password("adminpassword"),
        role_id=role.role_id,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_student_user(db_session: Session) -> User:
    role = db_session.query(Role).filter(Role.role_name == "STUDENT").first()
    user = User(
        name="Student User",
        email="student@dbit.in",
        password_hash=hash_password("studentpassword"),
        role_id=role.role_id,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_collector_user(db_session: Session) -> User:
    role = db_session.query(Role).filter(Role.role_name == "COLLECTOR").first()
    user = User(
        name="Collector User",
        email="collector@dbit.in",
        password_hash=hash_password("collectorpassword"),
        role_id=role.role_id,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_staff_user(db_session: Session) -> User:
    role = db_session.query(Role).filter(Role.role_name == "STAFF").first()
    user = User(
        name="Staff User",
        email="staff@dbit.in",
        password_hash=hash_password("staffpassword"),
        role_id=role.role_id,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_inactive_user(db_session: Session) -> User:
    role = db_session.query(Role).filter(Role.role_name == "STUDENT").first()
    user = User(
        name="Inactive Student",
        email="inactive@dbit.in",
        password_hash=hash_password("inactivepass123"),
        role_id=role.role_id,
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(test_admin_user: User) -> str:
    return create_access_token(
        subject=str(test_admin_user.user_id),
        role=test_admin_user.role.role_name,
    )


@pytest.fixture
def student_token(test_student_user: User) -> str:
    return create_access_token(
        subject=str(test_student_user.user_id),
        role=test_student_user.role.role_name,
    )


@pytest.fixture
def staff_token(test_staff_user: User) -> str:
    return create_access_token(
        subject=str(test_staff_user.user_id),
        role=test_staff_user.role.role_name,
    )


@pytest.fixture
def collector_token(test_collector_user: User) -> str:
    return create_access_token(
        subject=str(test_collector_user.user_id),
        role=test_collector_user.role.role_name,
    )


@pytest.fixture
def test_location(db_session: Session) -> Location:
    location = Location(
        name="Main Canteen",
        location_type="CANTEEN",
        building="Main Building",
        floor="Ground Floor",
        description="Central dining area",
        is_active=True,
    )
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location


@pytest.fixture
def test_waste_type(db_session: Session) -> WasteType:
    wt = db_session.query(WasteType).filter(WasteType.name == "WET_ORGANIC").first()
    if not wt:
        wt = WasteType(name="WET_ORGANIC", description="Organic waste", is_active=True)
        db_session.add(wt)
        db_session.commit()
        db_session.refresh(wt)
    return wt


@pytest.fixture
def test_bin(db_session: Session, test_location: Location, test_waste_type: WasteType) -> Bin:
    bin_obj = Bin(
        bin_code="TEST-BIN-01",
        location_id=test_location.location_id,
        waste_type_id=test_waste_type.waste_type_id,
        capacity_litres=Decimal("60.00"),
        current_fill_percentage=Decimal("45.50"),
        status="ACTIVE",
    )
    db_session.add(bin_obj)
    db_session.commit()
    db_session.refresh(bin_obj)
    return bin_obj


@pytest.fixture(autouse=True)
def reset_classifier_for_tests():
    """Ensure tests run against deterministic MockWasteClassifier unless explicitly overridden."""
    from ai.classification.model import MockWasteClassifier
    from app.services.classification_service import set_classifier

    set_classifier(MockWasteClassifier(model_version="v1.0-mock", confidence_threshold=0.70))
    yield
    set_classifier(None)

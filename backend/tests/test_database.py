import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User


def test_initial_roles_exist(db_session: Session) -> None:
    statement = select(Role.role_name)
    roles = db_session.scalars(statement).all()
    assert "STUDENT" in roles
    assert "STAFF" in roles
    assert "COLLECTOR" in roles
    assert "ADMIN" in roles
    assert len(roles) == 4


def test_user_creation_and_role_relationship(db_session: Session) -> None:
    role = db_session.scalar(select(Role).where(Role.role_name == "STAFF"))
    assert role is not None

    user = User(
        name="Staff Member",
        email="staff@dbit.in",
        password_hash=hash_password("staffpass123"),
        role_id=role.role_id,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.user_id is not None
    assert user.role.role_name == "STAFF"
    assert user.is_active is True
    assert user.created_at is not None


def test_user_email_uniqueness(db_session: Session) -> None:
    role = db_session.scalar(select(Role).where(Role.role_name == "STUDENT"))
    assert role is not None

    user1 = User(
        name="First Student",
        email="duplicate@dbit.in",
        password_hash=hash_password("pass1"),
        role_id=role.role_id,
    )
    db_session.add(user1)
    db_session.commit()

    user2 = User(
        name="Second Student",
        email="duplicate@dbit.in",
        password_hash=hash_password("pass2"),
        role_id=role.role_id,
    )
    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_role_name_uniqueness(db_session: Session) -> None:
    duplicate_role = Role(role_name="ADMIN")
    db_session.add(duplicate_role)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

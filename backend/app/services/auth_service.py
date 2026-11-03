import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.security import hash_password, verify_password
from app.models.role import Role
from app.models.user import User
from app.schemas.user import UserCreate


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    statement = (
        select(User)
        .options(joinedload(User.role))
        .where(User.email == email.strip().lower())
    )
    return db.scalar(statement)


def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    statement = (
        select(User)
        .options(joinedload(User.role))
        .where(User.user_id == user_id)
    )
    return db.scalar(statement)


def get_role_by_name(db: Session, role_name: str) -> Optional[Role]:
    statement = select(Role).where(Role.role_name == role_name.upper())
    return db.scalar(statement)


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_user(
    db: Session,
    name: str,
    email: str,
    password: str,
    role_name: str = "STUDENT",
    is_active: bool = True,
) -> User:
    role = get_role_by_name(db, role_name)
    if not role:
        raise ValueError(f"Role '{role_name}' does not exist.")

    user = User(
        name=name.strip(),
        email=email.strip().lower(),
        password_hash=hash_password(password),
        role_id=role.role_id,
        is_active=is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

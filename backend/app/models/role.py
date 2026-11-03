from typing import TYPE_CHECKING, List
from sqlalchemy import Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Role(Base):
    __tablename__ = "roles"

    role_id: Mapped[int] = mapped_column(
        SmallInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    role_name: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="role",
    )

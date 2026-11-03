from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, Integer, SmallInteger, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.bin import Bin
    from app.models.classification import WasteClassification


class WasteType(Base):
    __tablename__ = "waste_types"

    waste_type_id: Mapped[int] = mapped_column(
        SmallInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
        nullable=False,
    )

    bins: Mapped[List["Bin"]] = relationship(
        "Bin",
        back_populates="waste_type",
    )
    classifications: Mapped[List["WasteClassification"]] = relationship(
        "WasteClassification",
        back_populates="predicted_waste_type",
    )


from datetime import date
from typing import Optional
from uuid import uuid8

from sqlalchemy import UUID, BigInteger, Boolean, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    nid_path: Mapped[str] = mapped_column(String(255), nullable=True)

    nid_data: Mapped[Optional["NIDData"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class NIDData(Base):
    __tablename__ = "nid_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="nid_data")

    name_bn: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    fathers_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    mothers_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    dob: Mapped[date] = mapped_column(Date, nullable=False)
    nid: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )
    uuid: Mapped[str] = mapped_column(
        UUID,
        default=uuid8,
        nullable=False,
        index=True,
        unique=True,
    )

    @classmethod
    def string_to_date(cls, date_str: str) -> date:
        return date.fromisoformat(date_str)

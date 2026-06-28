"""Bonus / Spin models."""
from datetime import datetime
from sqlalchemy import Integer, BigInteger, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.base import Base


class BonusClaim(Base):
    __tablename__ = "bonus_claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    bonus_type: Mapped[str] = mapped_column(String(32))
    amount: Mapped[int] = mapped_column(Integer)
    metadata_json: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class DailySpin(Base):
    __tablename__ = "daily_spins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    spins_available: Mapped[int] = mapped_column(Integer, default=3)
    spins_used: Mapped[int] = mapped_column(Integer, default=0)
    last_reset: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
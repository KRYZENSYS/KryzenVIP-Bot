"""Achievement model."""
from datetime import datetime
from sqlalchemy import Integer, BigInteger, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.base import Base


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    code: Mapped[str] = mapped_column(String(32))
    title: Mapped[str] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(String(256), nullable=True)
    xp_reward: Mapped[int] = mapped_column(Integer, default=0)
    coin_reward: Mapped[int] = mapped_column(Integer, default=0)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
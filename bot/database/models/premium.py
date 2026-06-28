"""Premium subscription model."""
from datetime import datetime
from sqlalchemy import Integer, BigInteger, String, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.base import Base


class Premium(Base):
    __tablename__ = "premium"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    plan: Mapped[str] = mapped_column(String(16))
    price: Mapped[int] = mapped_column(Integer)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    payment_method: Mapped[str] = mapped_column(String(16))
    transaction_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False)
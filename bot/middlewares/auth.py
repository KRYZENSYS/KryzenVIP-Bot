"""Auth middleware - get/create User and inject into handler."""
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict
from loguru import logger

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy import select

from bot.database.models import User
from bot.config import settings


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user = data.get("event_from_user")
        session = data.get("session")
        if not tg_user or not session:
            return await handler(event, data)

        # Get or create
        stmt = select(User).where(User.tg_id == tg_user.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                tg_id=tg_user.id,
                username=tg_user.username,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
                language_code=tg_user.language_code or "uz",
                coins=100,
                xp=0,
                level=1,
                is_admin=tg_user.id in settings.parsed_admin_ids,
            )
            session.add(user)
            await session.flush()
            logger.info(f"New user: {user.tg_id}")
        else:
            user.last_active = datetime.utcnow()
            user.messages_count = (user.messages_count or 0) + 1
            user.username = tg_user.username or user.username
            user.first_name = tg_user.first_name or user.first_name
            user.last_name = tg_user.last_name or user.last_name

        # Process referral from deep-link
        if not user.referrer_id:
            text = getattr(event, "text", None) or ""
            if text.startswith("/start ref_"):
                try:
                    ref_id = int(text.split("ref_", 1)[1].split()[0])
                    if ref_id != user.tg_id and ref_id > 0:
                        user.referrer_id = ref_id
                        # Increment referrer count
                        ref_stmt = select(User).where(User.tg_id == ref_id)
                        ref_user = (await session.execute(ref_stmt)).scalar_one_or_none()
                        if ref_user:
                            ref_user.referral_count = (ref_user.referral_count or 0) + 1
                            ref_user.coins = (ref_user.coins or 0) + settings.REFERRAL_BONUS
                except (ValueError, IndexError):
                    pass

        # Check premium expiry
        if user.is_premium and user.premium_until and user.premium_until < datetime.utcnow():
            user.is_premium = False

        data["user"] = user
        return await handler(event, data)
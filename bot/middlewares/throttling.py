"""Rate limit / flood protection."""
import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from cachetools import TTLCache

from bot.config import settings


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.user_cache: TTLCache[int, list[float]] = TTLCache(maxsize=10_000, ttl=60)
        self.last_msg: TTLCache[int, float] = TTLCache(maxsize=10_000, ttl=30)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        user_id = user.id
        now = time.monotonic()

        last = self.last_msg.get(user_id, 0)
        if now - last < settings.FLOOD_PROTECTION_SECONDS:
            return None

        history = self.user_cache.get(user_id, [])
        history = [t for t in history if now - t < 60]
        if len(history) >= settings.RATE_LIMIT_PER_MINUTE:
            if isinstance(event, Message):
                await event.answer(
                    f"⏱ <b>Juda ko'p so'rov!</b>\n\n"
                    f"Limit: {settings.RATE_LIMIT_PER_MINUTE}/min",
                    parse_mode="HTML"
                )
            elif isinstance(event, CallbackQuery):
                await event.answer("⏱ Sekinroq!", show_alert=True)
            return None

        history.append(now)
        self.user_cache[user_id] = history
        self.last_msg[user_id] = now

        return await handler(event, data)
"""Ban check middleware."""
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from bot.config import settings


class BanCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("user")
        if user is None:
            return await handler(event, data)

        # Admin can bypass
        if user.tg_id in settings.parsed_admin_ids:
            return await handler(event, data)

        if user.is_banned:
            if isinstance(event, Message):
                await event.answer(
                    f"🚫 <b>Siz bloklangansiz</b>\n\n"
                    f"Sabab: {user.ban_reason or 'Noma\\'lum'}\n\n"
                    f"💬 Murojaat: @kryzen_support",
                    parse_mode="HTML"
                )
            elif isinstance(event, CallbackQuery):
                await event.answer("🚫 Bloklangansiz", show_alert=True)
            return None

        return await handler(event, data)
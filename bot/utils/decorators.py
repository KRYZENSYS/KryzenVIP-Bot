"""Decorators."""
from functools import wraps
from typing import Any, Awaitable, Callable

from aiogram.types import Message, CallbackQuery

from bot.config import settings


def admin_required(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    """Allow only admins."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        user = kwargs.get("user")
        event = args[0] if args else None

        # Determine admin status
        is_admin = False
        if user and getattr(user, "is_admin", False):
            is_admin = True
        elif event and getattr(event, "from_user", None):
            is_admin = event.from_user.id in settings.parsed_admin_ids

        if not is_admin:
            if isinstance(event, Message):
                await event.answer("🚫 <b>Ruxsat yo'q</b>", parse_mode="HTML")
            elif isinstance(event, CallbackQuery):
                await event.answer("🚫 Ruxsat yo'q", show_alert=True)
            return None

        return await func(*args, **kwargs)
    return wrapper
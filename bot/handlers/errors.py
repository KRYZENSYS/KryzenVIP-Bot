"""Global error handler."""
from aiogram import Dispatcher
from aiogram.types import ErrorEvent, Message, CallbackQuery
from loguru import logger


async def error_handler(event: ErrorEvent, **kwargs):
    logger.exception(f"Unhandled: {event.exception}\\nUpdate: {event.update}")

    if event.update.message:
        try:
            await event.update.message.answer(
                "❌ <b>Xato yuz berdi.</b>\n\nQaytadan urinib ko'ring yoki admin bilan bog'laning.\n\n💬 @kryzen_support"
            )
        except Exception:
            pass
    elif event.update.callback_query:
        try:
            await event.update.callback_query.answer("❌ Xato", show_alert=True)
        except Exception:
            pass


def register(dp: Dispatcher) -> None:
    dp.error.register(error_handler)
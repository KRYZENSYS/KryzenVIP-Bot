"""Settings handler."""
from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery

from bot.database.models import User
from bot.keyboards import back_to_main


async def toggle_lang(call: CallbackQuery, user: User, **kwargs):
    user.language_code = "en" if user.language_code == "uz" else "uz"
    await call.answer(f"🌐 Til: {user.language_code.upper()}", show_alert=True)


async def show_about(call: CallbackQuery, **kwargs):
    text = (
        "ℹ️ <b>KRYZEN VIP Bot</b>\n\n"
        "📌 v1.0.0 · aiogram 3.13 · SQLAlchemy 2.0\n"
        "🐳 Docker · Railway\n\n"
        "📞 @kryzen_support\n"
        "🌐 github.com/KRYZENSYS"
    )
    await call.message.edit_text(text, reply_markup=back_to_main())


def register(dp: Dispatcher) -> None:
    dp.callback_query.register(toggle_lang, F.data == "settings:lang")
    dp.callback_query.register(show_about, F.data == "settings:about")
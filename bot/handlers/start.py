"""Start and basic commands."""
from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.config import settings
from bot.database.models import User
from bot.keyboards import main_menu
from bot.utils.texts import T


async def cmd_start(message: Message, command: CommandObject, user: User, state: FSMContext, **kwargs):
    await state.clear()
    text = T.WELCOME.format(name=message.from_user.first_name or "Foydalanuvchi")
    await message.answer(text, reply_markup=main_menu(is_admin=user.is_admin))


async def cmd_help(message: Message, **kwargs):
    text = (
        "📖 <b>Yordam</b>\n\n"
        "🔹 /start — Bosh sahifa\n"
        "🔹 /profile — Profilim\n"
        "🔹 /premium — Premium tariflar\n"
        "🔹 /bonus — Kunlik bonus\n"
        "🔹 /referral — Referal tizimi\n"
        "🔹 /admin — Admin panel\n"
        "🔹 /help — Yordam\n\n"
        "💬 Savol: @kryzen_support"
    )
    await message.answer(text)


async def cmd_id(message: Message, **kwargs):
    await message.answer(f"🆔 Sizning ID: <code>{message.from_user.id}</code>")


async def cmd_cancel(message: Message, state: FSMContext, **kwargs):
    await state.clear()
    await message.answer("❌ Bekor qilindi", reply_markup=main_menu())


def register(dp: Dispatcher) -> None:
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_id, Command("id"))
    dp.message.register(cmd_cancel, Command("cancel"))
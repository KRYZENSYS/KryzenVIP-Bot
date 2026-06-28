"""Referral system handler."""
from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger
from sqlalchemy import select, desc, func

from bot.config import settings
from bot.database.models import User, Referral
from bot.keyboards import back_to_main


async def show_link(call: CallbackQuery, user: User, bot, **kwargs):
    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start=ref_{user.tg_id}"

    text = (
        f"🔗 <b>Sizning referal havolangiz:</b>\n\n<code>{link}</code>\n\n"
        f"🎁 Har bir do'st: <b>+{settings.REFERRAL_BONUS} 🪙</b>\n"
        f"💎 Premium do'st: <b>+{settings.REFERRAL_PREMIUM_BONUS} 🪙</b>\n\n"
        f"📊 Sizning referallar: <b>{user.referral_count}</b>"
    )
    await call.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📤 Ulashish", url=f"https://t.me/share/url?url={link}&text=Join%20KRYZEN%20VIP")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:referral")]
        ])
    )


async def show_stats(call: CallbackQuery, user: User, session, **kwargs):
    total_refs = (await session.execute(
        select(func.count(Referral.id)).where(Referral.referrer_id == user.tg_id)
    )).scalar() or 0

    text = (
        f"📊 <b>Referal statistikasi</b>\n\n"
        f"👥 Jami: <b>{total_refs}</b>\n"
        f"💰 Jami coin: <b>{total_refs * settings.REFERRAL_BONUS} 🪙</b>\n\n"
        f"⚡ Darajangiz:\n"
    )
    if total_refs >= 100:
        text += "👑 LEGEND — +1000 🪙"
    elif total_refs >= 50:
        text += "💎 DIAMOND — +500 🪙"
    elif total_refs >= 10:
        text += "🏆 GOLD — +200 🪙"
    elif total_refs >= 5:
        text += "⭐ SILVER — +100 🪙"
    elif total_refs >= 1:
        text += "🌱 BRONZE — +50 🪙"
    else:
        text += "🔒 Yangi boshlovchi"
    await call.message.edit_text(text, reply_markup=back_to_main())


async def show_top(call: CallbackQuery, session, **kwargs):
    top = list((await session.execute(
        select(User).order_by(desc(User.referral_count)).limit(10)
    )).scalars().all())

    text = "🏆 <b>Top referrer'lar</b>\n\n"
    medals = ["🥇", "🥈", "🥉"] + ["▫️"] * 7
    for i, u in enumerate(top):
        text += f"{medals[i]} <b>{u.first_name or 'User'}</b> — {u.referral_count} referal\n"
    await call.message.edit_text(text, reply_markup=back_to_main())


async def show_rewards(call: CallbackQuery, **kwargs):
    text = (
        f"💰 <b>Mukofotlar tizimi</b>\n\n"
        f"👤 1 referal: <b>+{settings.REFERRAL_BONUS} 🪙</b>\n"
        f"⭐ 5 referal: <b>+100 🪙</b>\n"
        f"🏆 10 referal: <b>+200 🪙</b>\n"
        f"💎 50 referal: <b>+500 🪙</b>\n"
        f"👑 100 referal: <b>+1000 🪙 + Premium</b>"
    )
    await call.message.edit_text(text, reply_markup=back_to_main())


def register(dp: Dispatcher) -> None:
    dp.callback_query.register(show_link,    F.data == "ref:link")
    dp.callback_query.register(show_stats,   F.data == "ref:stats")
    dp.callback_query.register(show_top,     F.data == "ref:top")
    dp.callback_query.register(show_rewards, F.data == "ref:rewards")
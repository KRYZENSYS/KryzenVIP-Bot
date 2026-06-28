"""Bonus - daily / spin / mystery box."""
import random
from datetime import datetime, timedelta
from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery
from loguru import logger
from sqlalchemy import select, desc, func

from bot.database.models import User, BonusClaim, DailySpin
from bot.services.achievements import unlock
from bot.keyboards import bonus_menu, back_to_main


DAILY_REWARDS = [50, 100, 150, 200, 300]
SPIN_REWARDS = [
    ("🪙 50 coin", 50),
    ("🪙 100 coin", 100),
    ("🪙 250 coin", 250),
    ("🪙 500 coin", 500),
    ("💎 Premium 1 kun", "premium_1d"),
    ("🎟 QR promo", "qr_promo"),
    ("❌ Yutqazdingiz", 0),
    ("🌟 100 XP", "xp"),
]
MYSTERY_REWARDS = [
    ("🪙 100 coin", 100),
    ("🪙 500 coin", 500),
    ("💎 Premium 7 kun", "premium_7d"),
    ("🌟 500 XP", "xp500"),
    ("🎁 1000 coin", 1000),
]


async def daily_bonus(call: CallbackQuery, user: User, session, **kwargs):
    now = datetime.utcnow()
    if user.last_bonus_date:
        diff = (now - user.last_bonus_date).total_seconds()
        if diff < 24 * 3600:
            remaining = 24 * 3600 - diff
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            await call.answer(f"⏱ Keyingi bonus: {hours}s {minutes}m", show_alert=True)
            return

    if user.last_bonus_date and (now - user.last_bonus_date).days == 1:
        user.daily_streak = (user.daily_streak or 0) + 1
    elif not user.last_bonus_date or (now - user.last_bonus_date).days > 1:
        user.daily_streak = 1

    base = random.choice(DAILY_REWARDS)
    streak_bonus = user.daily_streak * 20
    total = base + streak_bonus

    user.coins = (user.coins or 0) + total
    user.xp = (user.xp or 0) + 25
    user.last_bonus_date = now

    session.add(BonusClaim(user_id=user.tg_id, bonus_type="daily", amount=total))

    if user.daily_streak >= 3:
        await unlock(session, user, "STREAK_3")
    if user.daily_streak >= 7:
        await unlock(session, user, "STREAK_7")
    if user.daily_streak >= 30:
        await unlock(session, user, "STREAK_30")

    text = (
        f"🎁 <b>Kunlik bonus olindi!</b>\n\n"
        f"🪙 +{base} (asosiy)\n🔥 +{streak_bonus} (streak)\n"
        f"💰 <b>Jami: +{total} coin</b>\n\n"
        f"🔥 Streak: <b>{user.daily_streak} kun</b>\n📊 XP: +25"
    )
    await call.message.edit_text(text, reply_markup=bonus_menu())
    await call.answer(f"🎁 +{total} coin!")


async def spin_wheel(call: CallbackQuery, user: User, session, **kwargs):
    stmt = select(DailySpin).where(DailySpin.user_id == user.tg_id)
    spin = (await session.execute(stmt)).scalar_one_or_none()
    now = datetime.utcnow()

    if not spin:
        spin = DailySpin(user_id=user.tg_id, spins_available=3)
        session.add(spin)
    elif (now - spin.last_reset).days >= 1:
        spin.spins_available = 3
        spin.spins_used = 0
        spin.last_reset = now

    if spin.spins_used >= spin.spins_available:
        await call.answer(f"🎡 Spins tugadi: 0/{spin.spins_available}", show_alert=True)
        return

    spin.spins_used += 1
    weights = [25, 20, 15, 5, 3, 2, 25, 5]
    reward_text, reward_value = random.choices(SPIN_REWARDS, weights=weights)[0]

    actual = ""
    gained = 0
    if isinstance(reward_value, int):
        user.coins = (user.coins or 0) + reward_value
        gained = reward_value
        actual = f"🪙 <b>+{reward_value} coin</b>"
    elif reward_value == "premium_1d":
        user.is_premium = True
        user.premium_until = now + timedelta(days=1)
        actual = "💎 <b>Premium 1 kun!</b>"
    elif reward_value == "xp":
        user.xp = (user.xp or 0) + 100
        actual = "🌟 <b>+100 XP</b>"
    elif reward_value == "qr_promo":
        actual = "🎟 <b>QR promo (admin bilan)</b>"

    if gained > 0:
        session.add(BonusClaim(user_id=user.tg_id, bonus_type="spin", amount=gained))

    remaining = spin.spins_available - spin.spins_used
    text = (
        f"🎡 <b>Spin Wheel</b>\n\n"
        f"🎰 <b>{reward_text}</b>\n\n{actual}\n\n"
        f"📊 Spins: <b>{remaining}/{spin.spins_available}</b>"
    )
    await call.message.edit_text(text, reply_markup=bonus_menu())


async def mystery_box(call: CallbackQuery, user: User, session, **kwargs):
    if not user.is_premium:
        await call.answer("💎 Mystery Box faqat Premium uchun!", show_alert=True)
        return

    text_label, value = random.choice(MYSTERY_REWARDS)
    if isinstance(value, int):
        user.coins = (user.coins or 0) + value
        actual = f"🪙 <b>+{value} coin</b>"
    elif value == "premium_7d":
        user.is_premium = True
        if user.premium_until and user.premium_until > datetime.utcnow():
            user.premium_until += timedelta(days=7)
        else:
            user.premium_until = datetime.utcnow() + timedelta(days=7)
        actual = "💎 <b>Premium +7 kun</b>"
    elif value == "xp500":
        user.xp = (user.xp or 0) + 500
        actual = "🌟 <b>+500 XP</b>"

    session.add(BonusClaim(user_id=user.tg_id, bonus_type="mystery",
                            amount=value if isinstance(value, int) else 0))
    await call.message.edit_text(
        f"📦 <b>Mystery Box ochildi!</b>\n\n🎁 <b>{text_label}</b>\n\n{actual}",
        reply_markup=bonus_menu()
    )


async def show_top_winners(call: CallbackQuery, session, **kwargs):
    stmt = (
        select(
            User.tg_id, User.first_name, User.username,
            func.coalesce(func.sum(BonusClaim.amount), 0).label("total")
        )
        .join(BonusClaim, BonusClaim.user_id == User.tg_id)
        .group_by(User.tg_id, User.first_name, User.username)
        .order_by(desc("total"))
        .limit(10)
    )
    rows = (await session.execute(stmt)).all()

    text = "🏆 <b>Top bonus olganlar</b>\n\n"
    medals = ["🥇", "🥈", "🥉"] + ["▫️"] * 7
    if not rows:
        text += "Hozircha yo'q."
    for i, (tg_id, fname, uname, total) in enumerate(rows):
        text += f"{medals[i]} <b>{fname or 'User'}</b> — <code>{total}</code> 🪙\n"
    await call.message.edit_text(text, reply_markup=back_to_main())


def register(dp: Dispatcher) -> None:
    dp.callback_query.register(daily_bonus,      F.data == "bonus:daily")
    dp.callback_query.register(spin_wheel,       F.data == "bonus:spin")
    dp.callback_query.register(mystery_box,      F.data == "bonus:mystery")
    dp.callback_query.register(show_top_winners, F.data == "bonus:top")
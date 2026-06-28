"""Profile handler - avatar, stats, achievements."""
from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery
from sqlalchemy import select

from bot.database.models import User, Achievement
from bot.keyboards import profile_menu, back_to_main


async def show_avatar(call: CallbackQuery, user: User, **kwargs):
    photos = await call.bot.get_user_profile_photos(user.tg_id, limit=1)
    if photos.total_count > 0:
        await call.message.delete()
        await call.message.answer_photo(
            photos.photos[0][-1].file_id,
            caption=f"🖼 {user.first_name or 'User'}"
        )
        await call.message.answer("👤 Profil", reply_markup=profile_menu())
    else:
        await call.answer("📷 Avatar yo'q", show_alert=True)


async def show_stats(call: CallbackQuery, user: User, **kwargs):
    from bot.utils.levels import calculate_level
    text = (
        f"📊 <b>Batafsil statistika</b>\n\n"
        f"📈 Level: {calculate_level(user.xp)}\n"
        f"✨ XP: {user.xp}\n"
        f"🪙 Coins: {user.coins}\n"
        f"🔥 Streak: {user.daily_streak}\n"
        f"💬 Xabarlar: {user.messages_count}\n"
        f"📥 Yuklamalar: {user.downloads_count}\n"
        f"🤖 AI so'rovlar: {user.ai_requests_count}\n"
        f"👥 Referallar: {user.referral_count}"
    )
    await call.message.edit_text(text, reply_markup=back_to_main())


async def show_achievements(call: CallbackQuery, user: User, session, **kwargs):
    achievements = list((await session.execute(
        select(Achievement).where(Achievement.user_id == user.tg_id).order_by(Achievement.unlocked_at.desc()).limit(20)
    )).scalars().all())

    if not achievements:
        text = "🏆 <b>Achievements</b>\n\nHozircha yo'q. Botdan faol foydalaning!"
    else:
        text = f"🏆 <b>Achievements ({len(achievements)})</b>\n\n"
        for ach in achievements:
            text += f"✅ <b>{ach.title}</b>\n   <i>{ach.description}</i>\n   +{ach.xp_reward} XP, +{ach.coin_reward} 🪙\n\n"

    await call.message.edit_text(text, reply_markup=back_to_main())


def register(dp: Dispatcher) -> None:
    dp.callback_query.register(show_avatar, F.data == "profile:avatar")
    dp.callback_query.register(show_stats, F.data == "profile:stats")
    dp.callback_query.register(show_achievements, F.data == "profile:achievements")
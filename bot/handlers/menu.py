"""Main menu navigation callbacks."""
from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery
from loguru import logger

from bot.database.models import User
from bot.keyboards import (
    main_menu, ai_menu, tools_menu, cyber_menu, downloader_menu,
    premium_menu, profile_menu, referral_menu, bonus_menu, back_to_main,
)
from bot.utils.texts import T
from sqlalchemy import select, func, desc
from bot.database.models import User as UserModel


async def nav_home(call: CallbackQuery, user: User, **kwargs):
    text = T.WELCOME_BACK.format(
        premium="✅ Faol" if user.is_premium else "❌ Yo'q",
        coins=user.coins,
        level=user.level,
        streak=user.daily_streak,
    )
    await call.message.edit_text(text, reply_markup=main_menu(is_admin=user.is_admin))


async def menu_ai(call: CallbackQuery, **kwargs):
    text = (
        "🤖 <b>AI bo'limi</b>\n\n"
        "Sun'iy intellekt yordamida:\n"
        "• Suhbat va savol-javob\n"
        "• Kod yozish va tahlil\n"
        "• Matn, reklama, SEO\n"
        "• Tarjima (100+ til)\n"
        "• Prompt generator\n\n"
        "Funksiyani tanlang:"
    )
    await call.message.edit_text(text, reply_markup=ai_menu())


async def menu_tools(call: CallbackQuery, **kwargs):
    text = (
        "🛠 <b>Tools bo'limi</b>\n\n"
        "Foydali utility'lar:\n"
        "• QR/Barcode\n"
        "• Hash, Base64, JSON\n"
        "• Password generator\n"
        "• URL shortener\n\n"
        "Tanlang:"
    )
    await call.message.edit_text(text, reply_markup=tools_menu())


async def menu_cyber(call: CallbackQuery, **kwargs):
    text = (
        "🌐 <b>Cyber Tools</b>\n\n"
        "Tarmoq va xavfsizlik:\n"
        "• IP, DNS, WHOIS\n"
        "• SSL, HTTP Headers\n"
        "• Ping, Status\n\n"
        "⚠️ Faqat o'z resurslaringiz uchun ishlating."
    )
    await call.message.edit_text(text, reply_markup=cyber_menu())


async def menu_downloader(call: CallbackQuery, **kwargs):
    text = (
        "📥 <b>Downloader</b>\n\n"
        "Ijtimoiy tarmoqlardan yuklab oling:\n"
        "• Instagram, TikTok, YouTube\n"
        "• Facebook, Pinterest, Threads\n"
        "• Spotify metadata\n\n"
        "Havolani yuboring:"
    )
    await call.message.edit_text(text, reply_markup=downloader_menu())


async def menu_premium(call: CallbackQuery, **kwargs):
    text = (
        "💎 <b>Premium tariflar</b>\n\n"
        "💎 1 oy — 499 XTR\n"
        "💎 3 oy — 1299 XTR (tejash 30%)\n"
        "👑 Lifetime — 4999 XTR\n\n"
        "Premium bilan:\n" + T.PREMIUM_FEATURES
    )
    await call.message.edit_text(text, reply_markup=premium_menu())


async def menu_profile(call: CallbackQuery, user: User, **kwargs):
    from bot.utils.levels import calculate_level, progress_to_next_level
    from bot.utils.helpers import format_number

    cur_xp, next_xp, progress = progress_to_next_level(user.xp)
    lvl = calculate_level(user.xp)

    text = (
        f"👤 <b>Profil</b>\n\n"
        f"🆔 ID: <code>{user.tg_id}</code>\n"
        f"👤 @{user.username or '—'}\n"
        f"📛 {user.first_name or ''} {user.last_name or ''}\n\n"
        f"📊 Level: <b>{lvl}</b>\n"
        f"✨ XP: {format_number(user.xp)} / {format_number(next_xp)}\n\n"
        f"🪙 Coins: <b>{format_number(user.coins)}</b>\n"
        f"🔥 Streak: <b>{user.daily_streak} kun</b>\n"
        f"💎 Premium: {'✅ Faol' if user.is_premium else '❌ Yo\\'q'}\n\n"
        f"👥 Referallar: {user.referral_count}\n"
        f"📥 Yuklamalar: {user.downloads_count}\n"
        f"💬 Xabarlar: {user.messages_count}"
    )
    await call.message.edit_text(text, reply_markup=profile_menu())


async def menu_referral(call: CallbackQuery, **kwargs):
    text = (
        "👥 <b>Referal tizimi</b>\n\n"
        "Do'stlarni taklif qiling — tanga va XP oling!\n\n"
        "🎁 Har bir faol referal uchun: <b>100 coin</b>\n"
        "💎 Premium olgan referal uchun: <b>500 coin</b>\n\n"
        "Pastdagi tugmalar orqali boshqaring:"
    )
    await call.message.edit_text(text, reply_markup=referral_menu())


async def menu_bonus(call: CallbackQuery, user: User, **kwargs):
    text = (
        "🎁 <b>Kunlik Bonus</b>\n\n"
        f"🔥 Streak: <b>{user.daily_streak} kun</b>\n\n"
        "🎁 Kunlik bonus — har kuni 50-300 🪙\n"
        "🎡 Spin Wheel — har kuni 3 ta urinish\n"
        "📦 Mystery Box — har kuni Premium uchun\n\n"
        "Tanlang:"
    )
    await call.message.edit_text(text, reply_markup=bonus_menu())


async def menu_rating(call: CallbackQuery, session, **kwargs):
    stmt = select(UserModel).order_by(desc(UserModel.xp)).limit(10)
    top = (await session.execute(stmt)).scalars().all()

    text = "🏆 <b>Top 10 o'yinchilar (XP)</b>\n\n"
    medals = ["🥇", "🥈", "🥉"] + ["▫️"] * 7
    for i, u in enumerate(top):
        text += f"{medals[i]} <b>{u.first_name or 'User'}</b> — <code>{u.xp}</code> XP\n"

    text += "\n💎 XP to'plang va topga kiring!"
    await call.message.edit_text(text, reply_markup=back_to_main())


async def menu_admin(call: CallbackQuery, **kwargs):
    text = (
        "📞 <b>Aloqa</b>\n\n"
        "Savol yoki taklifingiz bormi?\n\n"
        "👤 Admin: @kryzen_support\n"
        "📢 Kanal: @kryzen_official\n"
        "💬 Chat: @kryzen_chat\n\n"
        "Yoki /admin (adminlar uchun)"
    )
    await call.message.edit_text(text, reply_markup=back_to_main())


async def menu_settings(call: CallbackQuery, **kwargs):
    text = (
        "⚙ <b>Sozlamalar</b>\n\n"
        "🌐 Til: O'zbek tili\n"
        "🔔 Bildirishnomalar: ✅\n\n"
        "Tez orada kengaytiriladi."
    )
    await call.message.edit_text(text, reply_markup=back_to_main())


def register(dp: Dispatcher) -> None:
    dp.callback_query.register(nav_home, F.data == "nav:home")
    dp.callback_query.register(menu_ai, F.data == "menu:ai")
    dp.callback_query.register(menu_tools, F.data == "menu:tools")
    dp.callback_query.register(menu_cyber, F.data == "menu:cyber")
    dp.callback_query.register(menu_downloader, F.data == "menu:downloader")
    dp.callback_query.register(menu_premium, F.data == "menu:premium")
    dp.callback_query.register(menu_profile, F.data == "menu:profile")
    dp.callback_query.register(menu_referral, F.data == "menu:referral")
    dp.callback_query.register(menu_bonus, F.data == "menu:bonus")
    dp.callback_query.register(menu_rating, F.data == "menu:rating")
    dp.callback_query.register(menu_admin, F.data == "menu:admin")
    dp.callback_query.register(menu_settings, F.data == "menu:settings")
"""Admin panel - stats, broadcast, ban, premium grant, promos, logs, backup, export."""
import asyncio
import csv
import io
import shutil
from datetime import datetime, timedelta

from aiogram import Dispatcher, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, BufferedInputFile
from loguru import logger
from sqlalchemy import select, func, desc

from bot.config import settings
from bot.database.models import User, Premium, Payment, ActionLog, PromoCode, PromoUsage
from bot.database.models.referral import Referral
from bot.utils.decorators import admin_required
from bot.states import AdminStates
from bot.keyboards import admin_menu, back_to_main


@admin_required
async def cmd_admin(message: Message, **kwargs):
    await message.answer("🔐 <b>Admin Panel</b>\n\nQuyidagilardan birini tanlang:", reply_markup=admin_menu())


async def show_panel(call: CallbackQuery, **kwargs):
    await call.message.edit_text("🔐 <b>Admin Panel</b>\n\nQuyidagilardan birini tanlang:", reply_markup=admin_menu())


@admin_required
async def admin_stats(call: CallbackQuery, session, **kwargs):
    total = (await session.execute(select(func.count(User.id)))).scalar() or 0
    today = (await session.execute(select(func.count(User.id)).where(User.created_at >= datetime.utcnow() - timedelta(days=1)))).scalar() or 0
    week = (await session.execute(select(func.count(User.id)).where(User.created_at >= datetime.utcnow() - timedelta(days=7)))).scalar() or 0
    premium = (await session.execute(select(func.count(User.id)).where(User.is_premium == True))).scalar() or 0
    banned = (await session.execute(select(func.count(User.id)).where(User.is_banned == True))).scalar() or 0
    total_coins = (await session.execute(select(func.coalesce(func.sum(User.coins), 0)))).scalar() or 0
    total_xp = (await session.execute(select(func.coalesce(func.sum(User.xp), 0)))).scalar() or 0
    total_rev = (await session.execute(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.status == "paid"))).scalar() or 0

    top = list((await session.execute(select(User).order_by(desc(User.xp)).limit(5))).scalars().all())
    top_text = "\n".join([f"{i+1}. {u.first_name or 'User'} — {u.xp} XP" for i, u in enumerate(top)])

    text = (
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Jami: <b>{total}</b> · Bugun: <b>{today}</b> · Hafta: <b>{week}</b>\n"
        f"💎 Premium: <b>{premium}</b> · 🚫 Ban: <b>{banned}</b>\n\n"
        f"🪙 Coins: <b>{total_coins:,}</b>\n"
        f"✨ XP: <b>{total_xp:,}</b>\n"
        f"💰 Daromad: <b>{total_rev:,} XTR</b>\n\n"
        f"🏆 <b>Top 5:</b>\n{top_text}"
    )
    await call.message.edit_text(text, reply_markup=admin_menu())


@admin_required
async def admin_users(call: CallbackQuery, session, **kwargs):
    users = list((await session.execute(select(User).order_by(desc(User.created_at)).limit(15))).scalars().all())
    text = "👥 <b>So'nggi 15 foydalanuvchi:</b>\n\n"
    for u in users:
        ban_mark = "🚫" if u.is_banned else ""
        prem_mark = "💎" if u.is_premium else ""
        text += f"{ban_mark}{prem_mark} <b>{u.first_name or 'User'}</b> (<code>{u.tg_id}</code>)\n   @{u.username or '—'} · {u.coins} 🪙\n"
    await call.message.edit_text(text, reply_markup=admin_menu())


@admin_required
async def admin_broadcast(call: CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state(AdminStates.broadcast_text)
    await call.message.edit_text(
        "📢 <b>Broadcast</b>\n\nXabarni yuboring. Markdown qo'llab-quvvatlanadi.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Bekor", callback_data="admin:panel")]])
    )


@admin_required
async def process_broadcast_text(message: Message, state: FSMContext, session, **kwargs):
    text = message.text or message.caption or ""
    if not text.strip():
        await message.answer("❌ Bo'sh xabar")
        await state.clear()
        return

    await state.update_data(broadcast_text=text, broadcast_entities=message.entities or message.caption_entities)
    total = (await session.execute(select(func.count(User.id)))).scalar() or 0
    await message.answer(
        f"📤 <b>Tasdiqlang:</b>\n\n👥 Qabul qiluvchilar: <b>{total}</b>\n\n{text}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Ha, yubor", callback_data="admin:broadcast:yes"),
             InlineKeyboardButton(text="❌ Yo'q", callback_data="admin:panel")]
        ])
    )
    await state.set_state(AdminStates.broadcast_confirm)


@admin_required
async def confirm_broadcast(call: CallbackQuery, state: FSMContext, bot: Bot, session, **kwargs):
    data = await state.get_data()
    text = data.get("broadcast_text", "")
    entities = data.get("broadcast_entities")
    if not text:
        await call.answer("❌ Bo'sh", show_alert=True)
        await state.clear()
        return

    status = await call.message.edit_text("📤 Yuborilmoqda...")

    users = list((await session.execute(select(User.tg_id).where(User.is_banned == False))).scalars().all())
    sent, failed = 0, 0
    for tg_id in users:
        try:
            await bot.send_message(tg_id, text, entities=entities)
            sent += 1
            if sent % 25 == 0:
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(0.05)
        except Exception as e:
            failed += 1
            logger.warning(f"Broadcast fail {tg_id}: {e}")

    await status.edit_text(f"✅ <b>Yakunlandi!</b>\n\n📤 Yuborildi: <b>{sent}</b>\n❌ Xato: <b>{failed}</b>")
    await state.clear()


@admin_required
async def admin_ban(call: CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state(AdminStates.ban_user)
    await call.message.edit_text("🚫 <b>Ban qilish</b>\n\nFoydalanuvchi ID sini yuboring:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Bekor", callback_data="admin:panel")]]))


@admin_required
async def process_ban(message: Message, state: FSMContext, session, **kwargs):
    try:
        tg_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Noto'g'ri ID")
        await state.clear()
        return
    user = (await session.execute(select(User).where(User.tg_id == tg_id))).scalar_one_or_none()
    if not user:
        await message.answer("❌ Topilmadi")
        await state.clear()
        return
    user.is_banned = True
    user.ban_reason = "Admin tomonidan"
    await message.answer(f"✅ <b>{user.first_name}</b> bloklandi", reply_markup=admin_menu())
    await state.clear()


@admin_required
async def admin_unban(call: CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state(AdminStates.unban_user)
    await call.message.edit_text("✅ <b>Unban</b>\n\nID yuboring:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Bekor", callback_data="admin:panel")]]))


@admin_required
async def process_unban(message: Message, state: FSMContext, session, **kwargs):
    try:
        tg_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Noto'g'ri ID")
        await state.clear()
        return
    user = (await session.execute(select(User).where(User.tg_id == tg_id))).scalar_one_or_none()
    if not user:
        await message.answer("❌ Topilmadi")
        await state.clear()
        return
    user.is_banned = False
    user.ban_reason = None
    await message.answer(f"✅ <b>{user.first_name}</b> blokdan chiqarildi", reply_markup=admin_menu())
    await state.clear()


@admin_required
async def admin_give_premium(call: CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state(AdminStates.give_premium)
    await call.message.edit_text("💎 <b>+Premium</b>\n\nFormat: `<id> <kunlar>`", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Bekor", callback_data="admin:panel")]]))


@admin_required
async def process_give_premium(message: Message, state: FSMContext, session, **kwargs):
    parts = message.text.strip().split()
    if len(parts) != 2:
        await message.answer("❌ Format: `<id> <kunlar>`")
        await state.clear()
        return
    try:
        tg_id, days = int(parts[0]), int(parts[1])
    except ValueError:
        await message.answer("❌ Son kerak")
        await state.clear()
        return
    user = (await session.execute(select(User).where(User.tg_id == tg_id))).scalar_one_or_none()
    if not user:
        await message.answer("❌ Topilmadi")
        await state.clear()
        return
    expires = datetime.utcnow() + timedelta(days=days)
    user.is_premium = True
    user.premium_until = expires
    user.premium_type = "admin"
    session.add(Premium(user_id=tg_id, plan=f"{days}d", price=0, expires_at=expires, payment_method="admin", is_active=True))
    await message.answer(f"✅ <b>{user.first_name}</b> ga {days} kun Premium berildi", reply_markup=admin_menu())
    await state.clear()


@admin_required
async def admin_create_promo(call: CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state(AdminStates.create_promo)
    await call.message.edit_text(
        "🎟 <b>Promo yaratish</b>\n\nFormat: `<code> <type> <value> <max_uses> [days]`\n\nMisollar:\n• WELCOME coins 100 100 30\n• VIP1M premium 1 50 30",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Bekor", callback_data="admin:panel")]])
    )


@admin_required
async def process_create_promo(message: Message, state: FSMContext, session, **kwargs):
    parts = message.text.strip().split()
    if len(parts) < 4:
        await message.answer("❌ Format: `<code> <type> <value> <max_uses>`")
        await state.clear()
        return
    code = parts[0].upper()
    reward_type = parts[1].lower()
    value = int(parts[2])
    max_uses = int(parts[3])
    days_valid = int(parts[4]) if len(parts) > 4 else 30

    if reward_type not in ("coins", "premium"):
        await message.answer("❌ Type: coins yoki premium")
        await state.clear()
        return

    expires = datetime.utcnow() + timedelta(days=days_valid)
    session.add(PromoCode(code=code, reward_type=reward_type, reward_value=value, max_uses=max_uses,
                          per_user_limit=1, is_active=True, expires_at=expires, created_by=message.from_user.id))
    await message.answer(
        f"✅ <b>Yaratildi!</b>\n\n🎟 <code>{code}</code>\n🎁 {reward_type} × {value}\n👥 Limit: {max_uses}\n📅 {days_valid} kun",
        reply_markup=admin_menu()
    )
    await state.clear()


@admin_required
async def admin_logs(call: CallbackQuery, session, **kwargs):
    logs = list((await session.execute(select(ActionLog).order_by(desc(ActionLog.created_at)).limit(20))).scalars().all())
    if not logs:
        await call.message.edit_text("📝 Loglar bo'sh", reply_markup=admin_menu())
        return
    text = "📝 <b>So'nggi 20 log:</b>\n\n"
    for log in logs:
        ts = log.created_at.strftime("%H:%M:%S")
        text += f"<code>{ts}</code> · <code>{log.user_id}</code> · <b>{log.action}</b>\n"
    await call.message.edit_text(text, reply_markup=admin_menu())


@admin_required
async def admin_backup(call: CallbackQuery, **kwargs):
    src = "data/kryzen.db"
    dst = f"data/backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.db"
    try:
        shutil.copy2(src, dst)
        await call.message.answer_document(FSInputFile(dst), caption=f"💾 Backup: {dst}")
    except Exception as e:
        await call.answer(f"❌ {e}", show_alert=True)


@admin_required
async def admin_export(call: CallbackQuery, session, **kwargs):
    users = list((await session.execute(select(User))).scalars().all())
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["ID", "TG_ID", "Username", "First", "Last", "Coins", "XP", "Premium", "Banned", "Created"])
    for u in users:
        writer.writerow([u.id, u.tg_id, u.username or "", u.first_name or "", u.last_name or "",
                          u.coins, u.xp, u.is_premium, u.is_banned, u.created_at.isoformat() if u.created_at else ""])
    await call.message.answer_document(
        BufferedInputFile(buf.getvalue().encode(), "users.csv"),
        caption=f"📊 {len(users)} ta user eksport"
    )


def register(dp: Dispatcher) -> None:
    dp.message.register(cmd_admin, Command("admin"))
    dp.callback_query.register(show_panel, F.data == "admin:panel")
    dp.callback_query.register(admin_stats, F.data == "admin:stats")
    dp.callback_query.register(admin_users, F.data == "admin:users")
    dp.callback_query.register(admin_broadcast, F.data == "admin:broadcast")
    dp.callback_query.register(confirm_broadcast, F.data == "admin:broadcast:yes")
    dp.callback_query.register(admin_ban, F.data == "admin:ban")
    dp.callback_query.register(admin_unban, F.data == "admin:unban")
    dp.callback_query.register(admin_give_premium, F.data == "admin:give_premium")
    dp.callback_query.register(admin_create_promo, F.data == "admin:create_promo")
    dp.callback_query.register(admin_logs, F.data == "admin:logs")
    dp.callback_query.register(admin_backup, F.data == "admin:backup")
    dp.callback_query.register(admin_export, F.data == "admin:export")

    dp.message.register(process_broadcast_text, AdminStates.broadcast_text)
    dp.message.register(process_ban, AdminStates.ban_user)
    dp.message.register(process_unban, AdminStates.unban_user)
    dp.message.register(process_give_premium, AdminStates.give_premium)
    dp.message.register(process_create_promo, AdminStates.create_promo)
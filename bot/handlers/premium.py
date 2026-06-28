"""Premium + promo handler (Telegram Stars)."""
from datetime import datetime, timedelta
from aiogram import Dispatcher, F, Bot
from aiogram.types import CallbackQuery, Message, LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from loguru import logger
from sqlalchemy import select

from bot.config import settings
from bot.database.models import User, Premium, PromoCode, PromoUsage
from bot.services.payment import payment_service
from bot.services.achievements import unlock
from bot.states import PremiumStates
from bot.keyboards import premium_menu, back_to_main


async def buy_premium(call: CallbackQuery, bot: Bot, user: User, **kwargs):
    plans = {
        "1month":   (settings.PREMIUM_PRICE_1MONTH,   "Premium · 1 oy"),
        "3months":  (settings.PREMIUM_PRICE_3MONTHS,  "Premium · 3 oy"),
        "lifetime": (settings.PREMIUM_PRICE_LIFETIME, "Premium · Lifetime"),
    }
    plan = call.data.replace("premium:", "")
    plan_data = plans.get(plan)
    if not plan_data:
        return
    price, title = plan_data

    sent = await payment_service.send_premium_invoice(
        bot=bot, chat_id=user.tg_id, plan=plan, price=price, user_id=user.tg_id,
    )
    if not sent:
        await call.message.answer("⚠️ To'lov xizmati vaqtincha ishlamayapti.")
    await call.answer()


async def premium_promo(call: CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state(PremiumStates.waiting_promo)
    await call.message.edit_text(
        "🎟 <b>Promo Code</b>\n\nPromo kodni yuboring.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Bekor", callback_data="menu:premium")]
        ])
    )


async def process_promo(message: Message, state: FSMContext, session, user: User, **kwargs):
    code = message.text.strip().upper()
    stmt = select(PromoCode).where(PromoCode.code == code, PromoCode.is_active == True)
    promo = (await session.execute(stmt)).scalar_one_or_none()

    if not promo:
        await message.answer("❌ Bunday promo kod mavjud emas.")
        await state.clear()
        return

    if promo.expires_at and promo.expires_at < datetime.utcnow():
        await message.answer("❌ Promo kod muddati tugagan.")
        await state.clear()
        return

    if promo.used_count >= promo.max_uses:
        await message.answer("❌ Promo kod limiti tugagan.")
        await state.clear()
        return

    usage_stmt = select(PromoUsage).where(
        PromoUsage.code_id == promo.id, PromoUsage.user_id == user.tg_id
    )
    usages = list((await session.execute(usage_stmt)).scalars().all())
    if len(usages) >= promo.per_user_limit:
        await message.answer("❌ Siz bu promo kodni ishlatgansiz.")
        await state.clear()
        return

    if promo.reward_type == "premium":
        days_map = {1: 30, 3: 90, 12: 365, 0: 36500}
        days = days_map.get(promo.reward_value, 30)
        expires = datetime.utcnow() + timedelta(days=days)

        user.is_premium = True
        user.premium_until = expires
        user.premium_type = "promo"

        new_premium = Premium(
            user_id=user.tg_id, plan="promo", price=0,
            expires_at=expires, payment_method="promo", is_active=True
        )
        session.add(new_premium)
        msg = f"💎 <b>Premium faollashtirildi!</b>\n\n📅 {expires.strftime('%Y-%m-%d')} gacha"
    else:
        user.coins = (user.coins or 0) + promo.reward_value
        msg = f"🪙 <b>+{promo.reward_value} coins</b>"

    promo.used_count += 1
    session.add(PromoUsage(code_id=promo.id, user_id=user.tg_id))

    await message.answer(msg, reply_markup=premium_menu())
    await unlock(session, user, "PREMIUM")
    await state.clear()


async def pre_checkout_handler(pre_checkout: PreCheckoutQuery, **kwargs):
    await payment_service.process_pre_checkout(pre_checkout)


async def successful_payment(message: Message, session, **kwargs):
    payment = message.successful_payment
    if not payment:
        return
    payload = payment.invoice_payload
    parts = payload.split(":")
    if len(parts) != 3 or parts[0] != "premium":
        return

    plan = parts[1]
    user_id = int(parts[2])
    success = await payment_service.process_successful_payment(session, user_id, plan, payment)

    if success:
        titles = {
            "1month":   "💎 Premium 1 oy",
            "3months":  "💎 Premium 3 oy",
            "lifetime": "👑 Premium Lifetime",
        }
        await message.answer(
            f"🎉 <b>Tabriklayman!</b>\n\n{titles.get(plan, 'Premium')} faollashtirildi!",
            reply_markup=premium_menu()
        )


async def show_features(call: CallbackQuery, **kwargs):
    text = (
        "💎 <b>Premium imkoniyatlari:</b>\n\n"
        "✅ Cheksiz AI\n✅ 50 MB gacha yuklab olish\n"
        "✅ Yuqori sifatli AI tasvir\n✅ Birinchi navbatda qo'llab-quvvatlash\n"
        "✅ Eksklyuziv achievement'lar\n✅ 2x XP va Coins\n"
        "✅ Reklama yo'q\n✅ Mystery Box har kuni"
    )
    await call.message.edit_text(text, reply_markup=premium_menu())


def register(dp: Dispatcher) -> None:
    dp.callback_query.register(buy_premium, F.data.in_({"premium:1month", "premium:3months", "premium:lifetime"}))
    dp.callback_query.register(premium_promo, F.data == "premium:promo")
    dp.callback_query.register(show_features, F.data == "premium:features")

    dp.message.register(process_promo, PremiumStates.waiting_promo)

    dp.pre_checkout_query.register(pre_checkout_handler)
    dp.message.register(successful_payment, F.successful_payment)
"""Payment service - Telegram Stars (XTR)."""
from datetime import datetime, timedelta
from loguru import logger
from aiogram import Bot
from aiogram.types import LabeledPrice, Message
from sqlalchemy import select

from bot.database.models import User, Premium, Payment


class PaymentService:
    async def send_premium_invoice(
        self, bot: Bot, chat_id: int, plan: str, price: int, user_id: int
    ) -> bool:
        try:
            await bot.send_invoice(
                chat_id=chat_id,
                title=f"💎 Premium · {plan}",
                description="KRYZEN VIP Premium — cheksiz AI, tools, va yuklab olish.",
                payload=f"premium:{plan}:{user_id}",
                provider_token="",
                currency="XTR",
                prices=[LabeledPrice(label=f"Premium {plan}", amount=price)],
            )
            return True
        except Exception as e:
            logger.error(f"Invoice send failed: {e}")
            return False

    async def process_pre_checkout(self, pre_checkout_query) -> None:
        await pre_checkout_query.answer(ok=True)

    async def process_successful_payment(
        self, session, user_id: int, plan: str, payment
    ) -> bool:
        try:
            stmt = select(User).where(User.tg_id == user_id)
            user = (await session.execute(stmt)).scalar_one_or_none()
            if not user:
                return False

            days_map = {"1month": 30, "3months": 90, "lifetime": 36500}
            days = days_map.get(plan, 30)
            expires = datetime.utcnow() + timedelta(days=days)

            user.is_premium = True
            user.premium_until = expires
            user.premium_type = plan

            new_premium = Premium(
                user_id=user_id,
                plan=plan,
                price=payment.total_amount,
                expires_at=expires,
                payment_method="stars",
                transaction_id=payment.telegram_payment_charge_id,
                is_active=True,
            )
            session.add(new_premium)

            pay_record = Payment(
                user_id=user_id,
                amount=payment.total_amount,
                currency="XTR",
                method="stars",
                transaction_id=payment.telegram_payment_charge_id,
                payload=f"premium:{plan}:{user_id}",
                status="paid",
                completed_at=datetime.utcnow(),
            )
            session.add(pay_record)

            logger.info(f"Payment OK: user={user_id} plan={plan} amount={payment.total_amount}")
            return True
        except Exception as e:
            logger.error(f"Payment process error: {e}")
            return False


payment_service = PaymentService()
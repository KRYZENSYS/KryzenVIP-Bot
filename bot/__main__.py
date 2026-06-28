"""KRYZEN VIP Telegram Bot — entry point."""
import asyncio
import sys
from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from loguru import logger

from bot.config import settings, setup_logging
from bot.database import init_db, close_db
from bot.handlers import register_all_handlers
from bot.middlewares import register_middlewares
from bot.services import init_services, close_services
from bot.utils.health import start_health_server


async def on_startup(bot: Bot) -> None:
    logger.info("🚀 KRYZEN VIP starting...")
    await init_db()
    await init_services()

    for admin_id in settings.parsed_admin_ids:
        with suppress(Exception):
            await bot.send_message(
                admin_id,
                "🟢 <b>KRYZEN VIP ishga tushdi</b>\n\n"
                f"🤖 Bot: @{settings.BOT_USERNAME}\n"
                "⚙ /admin",
                parse_mode=ParseMode.HTML
            )
    logger.success("✅ Bot ready")


async def on_shutdown(bot: Bot) -> None:
    logger.info("🛑 KRYZEN VIP shutting down...")
    for admin_id in settings.parsed_admin_ids:
        with suppress(Exception):
            await bot.send_message(admin_id, "🔴 <b>Bot to'xtatildi</b>", parse_mode=ParseMode.HTML)
    await close_services()
    await close_db()


async def main() -> None:
    setup_logging()
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    register_middlewares(dp)
    register_all_handlers(dp)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await bot.delete_webhook(drop_pending_updates=True)
    health_task = asyncio.create_task(start_health_server())

    try:
        logger.info("🤖 Polling started")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), polling_timeout=30)
    finally:
        health_task.cancel()
        with suppress(asyncio.CancelledError):
            await health_task
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("👋 Bye")
        sys.exit(0)
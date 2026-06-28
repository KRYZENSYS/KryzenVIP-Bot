"""All handlers registration."""
from aiogram import Dispatcher

from bot.handlers import start, menu, profile, ai, tools, cyber, downloader
from bot.handlers import premium, referral, bonus, admin, settings, errors


def register_all_handlers(dp: Dispatcher) -> None:
    errors.register(dp)
    admin.register(dp)
    start.register(dp)
    menu.register(dp)
    profile.register(dp)
    ai.register(dp)
    tools.register(dp)
    cyber.register(dp)
    downloader.register(dp)
    premium.register(dp)
    referral.register(dp)
    bonus.register(dp)
    settings.register(dp)
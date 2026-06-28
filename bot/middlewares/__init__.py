"""Middleware registration."""
from aiogram import Dispatcher

from bot.middlewares.db import DbSessionMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware
from bot.middlewares.auth import AuthMiddleware
from bot.middlewares.ban_check import BanCheckMiddleware


def register_middlewares(dp: Dispatcher) -> None:
    """Register middlewares. Order: outer → inner."""
    dp.message.middleware(BanCheckMiddleware())
    dp.callback_query.middleware(BanCheckMiddleware())

    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())

    dp.message.middleware(DbSessionMiddleware())
    dp.callback_query.middleware(DbSessionMiddleware())

    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
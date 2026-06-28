"""Achievement service - unlock and reward."""
from datetime import datetime
from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from bot.database.models import User, Achievement


ACHIEVEMENTS = {
    "FIRST_CHAT":     {"title": "💬 Birinchi suhbat",   "desc": "AI bilan birinchi chat",            "xp": 50,   "coin": 10},
    "FIRST_DL":       {"title": "📥 Birinchi yuklab",    "desc": "Birinchi yuklab olish",              "xp": 30,   "coin": 5},
    "DOWNLOAD_10":    {"title": "📦 10 ta yuklab",       "desc": "10 ta yuklab oldingiz",              "xp": 100,  "coin": 50},
    "DOWNLOAD_100":   {"title": "🏆 100 ta yuklab",      "desc": "100 ta yuklab oldingiz",             "xp": 500,  "coin": 200},
    "STREAK_3":       {"title": "🔥 3 kunlik streak",   "desc": "3 kunlik streak",                    "xp": 50,   "coin": 30},
    "STREAK_7":       {"title": "🌟 7 kunlik streak",   "desc": "7 kunlik streak",                    "xp": 150,  "coin": 100},
    "STREAK_30":      {"title": "👑 30 kunlik streak",  "desc": "30 kunlik streak",                   "xp": 1000, "coin": 500},
    "PREMIUM":        {"title": "💎 Premium",            "desc": "Premium faollashtirildi",            "xp": 200,  "coin": 100},
    "REFERRAL_5":     {"title": "👥 5 referal",          "desc": "5 ta do'st taklif qildingiz",        "xp": 200,  "coin": 100},
    "REFERRAL_25":    {"title": "⭐ 25 referal",         "desc": "25 ta do'st taklif qildingiz",       "xp": 500,  "coin": 300},
    "REFERRAL_100":   {"title": "👑 100 referal",        "desc": "100 ta do'st taklif qildingiz",      "xp": 2000, "coin": 1500},
    "LEVEL_5":        {"title": "📈 Level 5",            "desc": "5-levelga yetdingiz",                "xp": 0,    "coin": 100},
    "LEVEL_10":       {"title": "🌟 Level 10",           "desc": "10-levelga yetdingiz",               "xp": 0,    "coin": 300},
    "LEVEL_25":       {"title": "💎 Level 25",           "desc": "25-levelga yetdingiz",               "xp": 0,    "coin": 1000},
}


async def unlock(session, user: User, code: str) -> bool:
    """Unlock achievement if not already unlocked."""
    config = ACHIEVEMENTS.get(code)
    if not config:
        return False

    stmt = select(Achievement).where(
        Achievement.user_id == user.tg_id,
        Achievement.code == code,
    )
    existing = (await session.execute(stmt)).scalar_one_or_none()
    if existing:
        return False

    ach = Achievement(
        user_id=user.tg_id,
        code=code,
        title=config["title"],
        description=config["desc"],
        xp_reward=config["xp"],
        coin_reward=config["coin"],
        unlocked_at=datetime.utcnow(),
    )
    session.add(ach)
    try:
        await session.flush()
    except IntegrityError:
        return False

    user.xp = (user.xp or 0) + config["xp"]
    user.coins = (user.coins or 0) + config["coin"]

    logger.info(f"Achievement: {user.tg_id} unlocked {code}")
    return True


class AchievementService:
    async def list_user(self, session, user_id: int) -> list[Achievement]:
        stmt = select(Achievement).where(Achievement.user_id == user_id).order_by(Achievement.unlocked_at.desc())
        return list((await session.execute(stmt)).scalars().all())
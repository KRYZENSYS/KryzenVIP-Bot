"""KRYZEN VIP — Application configuration."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List

from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    BOT_TOKEN: str = Field(..., min_length=20)
    BOT_USERNAME: str = "KRYZENBot"
    ADMIN_IDS: str = ""

    DATABASE_URL: str = "sqlite+aiosqlite:///data/kryzen.db"
    REDIS_URL: str = ""

    OPENAI_API_KEY: str = ""
    DEEPAI_API_KEY: str = ""
    STABILITY_API_KEY: str = ""

    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    TIMEZONE: str = "Asia/Tashkent"

    PREMIUM_PRICE_1MONTH: int = 499
    PREMIUM_PRICE_3MONTHS: int = 1299
    PREMIUM_PRICE_LIFETIME: int = 4999

    REFERRAL_BONUS: int = 100
    REFERRAL_PREMIUM_BONUS: int = 500

    RATE_LIMIT_PER_MINUTE: int = 20
    FLOOD_PROTECTION_SECONDS: int = 2

    REQUIRED_CHANNELS: str = ""
    SECRET_KEY: str = "change-me-in-production"

    @property
    def parsed_admin_ids(self) -> List[int]:
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip().isdigit()]

    @property
    def parsed_required_channels(self) -> List[str]:
        return [x.strip() for x in self.REQUIRED_CHANNELS.split(",") if x.strip()]


settings = Settings()


def setup_logging() -> None:
    LOG_DIR = BASE_DIR / "logs"
    LOG_DIR.mkdir(exist_ok=True)

    logger.remove()

    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
               "<level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
    )

    logger.add(
        LOG_DIR / "bot.log",
        rotation="50 MB",
        retention="14 days",
        compression="zip",
        level="DEBUG" if settings.DEBUG else "INFO",
        enqueue=True,
    )

    logger.add(
        LOG_DIR / "errors.log",
        rotation="20 MB",
        retention="30 days",
        compression="zip",
        level="ERROR",
        backtrace=True,
        diagnose=settings.DEBUG,
    )

    logger.info(f"📝 Logging configured: {settings.LOG_LEVEL}")
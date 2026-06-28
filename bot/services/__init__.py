"""Service singletons."""
from typing import Optional
from aiohttp import ClientSession

from bot.services.ai_service import AIService
from bot.services.downloader import Downloader
from bot.services.payment import PaymentService
from bot.services.achievements import AchievementService


_ai: Optional[AIService] = None
_downloader: Optional[Downloader] = None
_payment: Optional[PaymentService] = None
_achievements: Optional[AchievementService] = None
_http: Optional[ClientSession] = None


async def init_services() -> None:
    global _ai, _downloader, _payment, _achievements, _http

    _http = ClientSession(timeout=ClientTimeout(total=60))
    _ai = AIService()
    _downloader = Downloader()
    _payment = PaymentService()
    _achievements = AchievementService()


async def close_services() -> None:
    global _http
    if _http and not _http.closed:
        await _http.close()


def get_http() -> Optional[ClientSession]:
    return _http


def get_ai() -> AIService:
    assert _ai is not None, "AI service not initialized"
    return _ai


def get_downloader() -> Downloader:
    assert _downloader is not None, "Downloader not initialized"
    return _downloader


def get_payment() -> PaymentService:
    assert _payment is not None, "Payment service not initialized"
    return _payment


def get_achievements() -> AchievementService:
    assert _achievements is not None, "Achievement service not initialized"
    return _achievements


from aiohttp import ClientTimeout
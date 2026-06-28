"""Tiny aiohttp health server for Docker/Railway."""
from aiohttp import web
from loguru import logger


async def health_handler(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok", "bot": "kryzen"})


async def start_health_server() -> None:
    app = web.Application()
    app.router.add_get("/health", health_handler)
    app.router.add_get("/", lambda r: web.Response(text="KRYZEN VIP Bot is running"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    logger.info("🏥 Health server on :8080/health")
    import asyncio
    while True:
        await asyncio.sleep(3600)
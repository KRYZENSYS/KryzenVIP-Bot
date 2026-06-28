"""Downloader handler - 8 platforms via yt-dlp."""
from aiogram import Dispatcher, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.enums import ChatAction
from loguru import logger

from bot.database.models import User
from bot.services.downloader import downloader
from bot.services.achievements import unlock
from bot.states import DownloadStates
from bot.keyboards import downloader_menu


DL_MAP = {
    "dl:instagram": ("instagram", "📸 Instagram video/reel linkini yuboring:"),
    "dl:tiktok":    ("tiktok",    "🎵 TikTok video linkini yuboring:"),
    "dl:youtube":   ("youtube",   "▶️ YouTube video linkini yuboring:"),
    "dl:facebook":  ("facebook",  "📘 Facebook video linkini yuboring:"),
    "dl:pinterest": ("pinterest", "📌 Pinterest pin linkini yuboring:"),
    "dl:threads":   ("threads",   "🧵 Threads post linkini yuboring:"),
    "dl:spotify":   ("spotify",   "🎧 Spotify track linkini yuboring (metadata):"),
    "dl:telegram":  ("telegram",  "✈️ Telegram media linkini yuboring:"),
}


async def dl_select(call: CallbackQuery, state: FSMContext, **kwargs):
    config = DL_MAP.get(call.data)
    if not config:
        return
    platform, prompt = config
    await state.update_data(platform=platform)
    await state.set_state(DownloadStates.waiting_url)
    await call.message.edit_text(
        prompt,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Bekor", callback_data="menu:downloader")]
        ])
    )


async def process_url(message: Message, state: FSMContext, user: User, session, bot: Bot, **kwargs):
    url = message.text.strip()
    if not url.startswith(("http://", "https://", "t.me")):
        await message.answer("❌ Noto'g'ri havola")
        await state.clear()
        return

    data = await state.get_data()
    platform = data.get("platform", "auto")

    if platform == "telegram" or url.startswith("t.me/"):
        await message.answer(
            "✈️ <b>Telegram yuklab olish:</b>\n\n"
            "⚠️ Ochiq postlardan yuklab oling — Telegram ilovasida saqlang.\n"
            "Yopiq kanallardan faqat kanal egasi yuklab oladi.",
            reply_markup=downloader_menu()
        )
        await state.clear()
        return

    await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)
    status = await message.answer("⏳ Yuklanmoqda...")

    try:
        path = await downloader.download(url, platform)
        if not path or not path.exists():
            await status.edit_text("❌ Yuklab bo'lmadi. URL tekshiring yoki kontent yopiq.")
            await state.clear()
            return

        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > 50:
            await status.edit_text(f"❌ Fayl katta: {size_mb:.1f} MB (limit: 50 MB)")
            path.unlink(missing_ok=True)
            await state.clear()
            return

        ext = path.suffix.lower()
        await status.delete()
        caption = f"✅ Yuklandi · {platform} · {size_mb:.1f} MB"

        if ext in [".mp4", ".mov", ".webm", ".mkv"]:
            await message.answer_video(FSInputFile(str(path)), caption=caption)
        elif ext in [".mp3", ".m4a", ".ogg", ".wav"]:
            await message.answer_audio(FSInputFile(str(path)), caption=caption)
        elif ext in [".jpg", ".jpeg", ".png", ".webp"]:
            await message.answer_photo(FSInputFile(str(path)), caption=caption)
        else:
            await message.answer_document(FSInputFile(str(path)), caption=caption)

        user.downloads_count = (user.downloads_count or 0) + 1
        user.xp = (user.xp or 0) + 10
        user.coins = (user.coins or 0) + 5

        await unlock(session, user, "FIRST_DL")
        if user.downloads_count >= 10:
            await unlock(session, user, "DOWNLOAD_10")
        if user.downloads_count >= 100:
            await unlock(session, user, "DOWNLOAD_100")

        try:
            path.unlink()
        except Exception:
            pass

        await message.answer("📥 Yana yuklash:", reply_markup=downloader_menu())

    except Exception as e:
        logger.error(f"Download error: {e}")
        await status.edit_text(f"❌ Xato: {str(e)[:200]}")
    await state.clear()


def register(dp: Dispatcher) -> None:
    for cb in DL_MAP.keys():
        dp.callback_query.register(dl_select, F.data == cb)
    dp.message.register(process_url, DownloadStates.waiting_url)
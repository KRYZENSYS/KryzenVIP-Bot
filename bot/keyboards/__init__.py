"""Inline + Reply keyboards."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="🤖 AI", callback_data="menu:ai"),
            InlineKeyboardButton(text="🛠 Tools", callback_data="menu:tools"),
        ],
        [
            InlineKeyboardButton(text="🌐 Cyber", callback_data="menu:cyber"),
            InlineKeyboardButton(text="📥 Downloader", callback_data="menu:downloader"),
        ],
        [
            InlineKeyboardButton(text="👤 Profil", callback_data="menu:profile"),
            InlineKeyboardButton(text="💎 Premium", callback_data="menu:premium"),
        ],
        [
            InlineKeyboardButton(text="🎁 Bonus", callback_data="menu:bonus"),
            InlineKeyboardButton(text="👥 Referral", callback_data="menu:referral"),
        ],
        [
            InlineKeyboardButton(text="🏆 Top", callback_data="menu:rating"),
            InlineKeyboardButton(text="⚙ Sozlamalar", callback_data="menu:settings"),
        ],
    ]
    if is_admin:
        rows.append([InlineKeyboardButton(text="🔐 Admin", callback_data="admin:panel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def ai_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 AI Chat", callback_data="ai:chat"),
         InlineKeyboardButton(text="🎨 Image Prompt", callback_data="ai:image_prompt")],
        [InlineKeyboardButton(text="⌨️ Kod yozish", callback_data="ai:code"),
         InlineKeyboardButton(text="🔍 Kod review", callback_data="ai:code_review")],
        [InlineKeyboardButton(text="📝 Matn", callback_data="ai:write"),
         InlineKeyboardButton(text="🌍 Tarjima", callback_data="ai:translate")],
        [InlineKeyboardButton(text="📄 Rezyume", callback_data="ai:resume"),
         InlineKeyboardButton(text="📢 Reklama", callback_data="ai:ads")],
        [InlineKeyboardButton(text="🔎 SEO", callback_data="ai:seo"),
         InlineKeyboardButton(text="⚡ Prompt gen", callback_data="ai:prompt_gen")],
        [InlineKeyboardButton(text="🔙 Asosiy", callback_data="nav:home")],
    ])


def tools_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔳 QR", callback_data="tool:qr"),
         InlineKeyboardButton(text="🔤 Base64", callback_data="tool:base64")],
        [InlineKeyboardButton(text="🔑 Parol", callback_data="tool:password")],
        [InlineKeyboardButton(text="📋 JSON", callback_data="tool:json"),
         InlineKeyboardButton(text="#️⃣ Hash", callback_data="tool:hash")],
        [InlineKeyboardButton(text="🔗 URL short", callback_data="tool:urlshort")],
        [InlineKeyboardButton(text="🔙 Asosiy", callback_data="nav:home")],
    ])


def cyber_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 IP", callback_data="cyber:ip"),
         InlineKeyboardButton(text="🌐 DNS", callback_data="cyber:dns")],
        [InlineKeyboardButton(text="📋 WHOIS", callback_data="cyber:whois"),
         InlineKeyboardButton(text="🔒 SSL", callback_data="cyber:ssl")],
        [InlineKeyboardButton(text="📨 Headers", callback_data="cyber:headers"),
         InlineKeyboardButton(text="🌍 Status", callback_data="cyber:status")],
        [InlineKeyboardButton(text="🤖 UA parse", callback_data="cyber:ua")],
        [InlineKeyboardButton(text="🔙 Asosiy", callback_data="nav:home")],
    ])


def downloader_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Instagram", callback_data="dl:instagram"),
         InlineKeyboardButton(text="🎵 TikTok", callback_data="dl:tiktok")],
        [InlineKeyboardButton(text="▶️ YouTube", callback_data="dl:youtube"),
         InlineKeyboardButton(text="📘 Facebook", callback_data="dl:facebook")],
        [InlineKeyboardButton(text="📌 Pinterest", callback_data="dl:pinterest"),
         InlineKeyboardButton(text="🧵 Threads", callback_data="dl:threads")],
        [InlineKeyboardButton(text="🎧 Spotify", callback_data="dl:spotify"),
         InlineKeyboardButton(text="✈️ Telegram", callback_data="dl:telegram")],
        [InlineKeyboardButton(text="🔙 Asosiy", callback_data="nav:home")],
    ])


def premium_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 1 oy — 499 XTR", callback_data="premium:1month")],
        [InlineKeyboardButton(text="💎 3 oy — 1299 XTR", callback_data="premium:3months")],
        [InlineKeyboardButton(text="👑 Lifetime — 4999 XTR", callback_data="premium:lifetime")],
        [InlineKeyboardButton(text="🎟 Promo code", callback_data="premium:promo"),
         InlineKeyboardButton(text="ℹ️ Imkoniyatlar", callback_data="premium:features")],
        [InlineKeyboardButton(text="🔙 Asosiy", callback_data="nav:home")],
    ])


def profile_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🖼 Avatar", callback_data="profile:avatar"),
         InlineKeyboardButton(text="📊 Stat", callback_data="profile:stats")],
        [InlineKeyboardButton(text="🏆 Achievements", callback_data="profile:achievements")],
        [InlineKeyboardButton(text="🔙 Asosiy", callback_data="nav:home")],
    ])


def referral_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Havolam", callback_data="ref:link"),
         InlineKeyboardButton(text="📊 Statistika", callback_data="ref:stats")],
        [InlineKeyboardButton(text="🏆 Top", callback_data="ref:top"),
         InlineKeyboardButton(text="💰 Mukofotlar", callback_data="ref:rewards")],
        [InlineKeyboardButton(text="🔙 Asosiy", callback_data="nav:home")],
    ])


def bonus_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Kunlik bonus", callback_data="bonus:daily")],
        [InlineKeyboardButton(text="🎡 Spin Wheel", callback_data="bonus:spin")],
        [InlineKeyboardButton(text="📦 Mystery Box (💎)", callback_data="bonus:mystery")],
        [InlineKeyboardButton(text="🏆 Top winners", callback_data="bonus:top")],
        [InlineKeyboardButton(text="🔙 Asosiy", callback_data="nav:home")],
    ])


def admin_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin:stats"),
         InlineKeyboardButton(text="👥 Users", callback_data="admin:users")],
        [InlineKeyboardButton(text="📢 Broadcast", callback_data="admin:broadcast")],
        [InlineKeyboardButton(text="🚫 Ban", callback_data="admin:ban"),
         InlineKeyboardButton(text="✅ Unban", callback_data="admin:unban")],
        [InlineKeyboardButton(text="💎 +Premium", callback_data="admin:give_premium"),
         InlineKeyboardButton(text="🎟 +Promo", callback_data="admin:create_promo")],
        [InlineKeyboardButton(text="📝 Logs", callback_data="admin:logs")],
        [InlineKeyboardButton(text="💾 Backup", callback_data="admin:backup"),
         InlineKeyboardButton(text="📤 Export CSV", callback_data="admin:export")],
        [InlineKeyboardButton(text="🔙 Asosiy", callback_data="nav:home")],
    ])


def back_to_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="nav:home")]
    ])


def back_to(target: str = "menu:ai") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data=target)]
    ])
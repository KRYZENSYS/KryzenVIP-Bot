"""Cyber Tools handlers - IP, DNS, WHOIS, SSL, etc."""
import socket
import time
from aiohttp import ClientTimeout

from aiogram import Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.services import get_http
from bot.states import CyberStates
from bot.keyboards import cyber_menu


CYBER_MAP = {
    "cyber:ip":      (CyberStates.ip,      "🔍 IP yoki domen yuboring:"),
    "cyber:dns":     (CyberStates.dns,     "🌐 Domen yuboring (masalan: google.com):"),
    "cyber:whois":   (CyberStates.whois,   "📋 Domen yuboring:"),
    "cyber:ssl":     (CyberStates.ssl,     "🔒 Domen yuboring:"),
    "cyber:headers": (CyberStates.headers, "📨 URL yuboring:"),
    "cyber:status":  (CyberStates.status,  "🌍 URL yuboring (https://...):"),
    "cyber:ua":      (CyberStates.ua,      "🤖 User-Agent string yuboring:"),
}


async def cyber_select(call: CallbackQuery, state: FSMContext, **kwargs):
    config = CYBER_MAP.get(call.data)
    if not config:
        return
    s, prompt = config
    await state.set_state(s)
    await call.message.edit_text(
        prompt,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Bekor", callback_data="menu:cyber")]
        ])
    )


async def cyber_ip(message: Message, state: FSMContext):
    target = message.text.strip()
    http = get_http()
    if not http:
        await message.answer("❌ HTTP xizmati mavjud emas")
        await state.clear()
        return
    try:
        async with http.get(f"http://ip-api.com/json/{target}") as resp:
            data = await resp.json(content_type=None)
            if data.get("status") == "success":
                text = (
                    f"🔍 <b>IP Lookup</b>\n\n"
                    f"IP: <code>{data.get('query')}</code>\n"
                    f"🌍 Mamlakat: {data.get('country')}\n"
                    f"🏙 Mintaqa: {data.get('regionName')}\n"
                    f"📍 Shahar: {data.get('city')}\n"
                    f"📮 ZIP: {data.get('zip')}\n"
                    f"📡 ISP: {data.get('isp')}\n"
                    f"🏢 Org: {data.get('org')}\n"
                    f"⏱ TZ: {data.get('timezone')}"
                )
            else:
                text = f"❌ Topilmadi: {target}"
    except Exception as e:
        text = f"❌ Xato: {e}"
    await message.answer(text, reply_markup=cyber_menu())
    await state.clear()


async def cyber_dns(message: Message, state: FSMContext):
    domain = message.text.strip().replace("https://", "").replace("http://", "").split("/")[0]
    try:
        infos = socket.getaddrinfo(domain, None)
        unique_ips = list({ip[4][0] for ip in infos})
        text = f"🌐 <b>DNS Lookup</b>\n\nDomen: <code>{domain}</code>\n\n"
        for ip in unique_ips[:10]:
            text += f"• <code>{ip}</code>\n"
    except Exception as e:
        text = f"❌ Xato: {e}"
    await message.answer(text, reply_markup=cyber_menu())
    await state.clear()


async def cyber_whois(message: Message, state: FSMContext):
    domain = message.text.strip().replace("https://", "").replace("http://", "").split("/")[0]
    await message.answer(
        f"📋 <b>WHOIS:</b>\n\nDomen: <code>{domain}</code>\n\n"
        f"⚠️ WHOIS API kaliti kerak. Istalgan bepul WHOIS servisdan foydalaning:\n"
        f"🔗 who.is/whois/{domain}",
        reply_markup=cyber_menu()
    )
    await state.clear()


async def cyber_ssl(message: Message, state: FSMContext):
    domain = message.text.strip().replace("https://", "").replace("http://", "").split("/")[0]
    http = get_http()
    if not http:
        await message.answer("❌ HTTP xizmati mavjud emas")
        await state.clear()
        return
    try:
        async with http.get(f"https://ssl-checker.io/api/v1/check/{domain}") as resp:
            data = await resp.json(content_type=None)
            if data.get("result") == "success":
                text = (
                    f"🔒 <b>SSL Check</b>\n\n"
                    f"Domen: <code>{domain}</code>\n"
                    f"Status: ✅ Valid\n"
                    f"Issuer: {data.get('issued_by', 'N/A')}\n"
                    f"Valid from: {data.get('valid_from', 'N/A')}\n"
                    f"Valid to: {data.get('valid_till', 'N/A')}"
                )
            else:
                text = f"⚠️ SSL topilmadi: {domain}"
    except Exception as e:
        text = f"❌ Xato: {e}"
    await message.answer(text, reply_markup=cyber_menu())
    await state.clear()


async def cyber_headers(message: Message, state: FSMContext):
    url = message.text.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    http = get_http()
    if not http:
        await message.answer("❌ HTTP xizmati mavjud emas")
        await state.clear()
        return
    try:
        async with http.get(url) as resp:
            text = f"📨 <b>HTTP Headers</b>\n\nURL: <code>{url}</code>\nStatus: {resp.status}\n\n"
            for k, v in resp.headers.items():
                if len(text) > 3500:
                    text += "\n... (kesildi)"
                    break
                text += f"<b>{k}:</b> <code>{v[:80]}</code>\n"
    except Exception as e:
        text = f"❌ Xato: {e}"
    await message.answer(text, reply_markup=cyber_menu())
    await state.clear()


async def cyber_status(message: Message, state: FSMContext):
    url = message.text.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    http = get_http()
    if not http:
        await message.answer("❌ HTTP xizmati mavjud emas")
        await state.clear()
        return
    try:
        start = time.time()
        async with http.get(url, timeout=ClientTimeout(total=10)) as resp:
            elapsed = (time.time() - start) * 1000
            text = (
                f"🌍 <b>Site Status</b>\n\n"
                f"URL: <code>{url}</code>\n"
                f"Status: <b>{resp.status}</b>\n"
                f"Ping: {elapsed:.0f} ms\n"
                f"Server: {resp.headers.get('Server', 'N/A')}\n"
                f"Content-Type: {resp.headers.get('Content-Type', 'N/A')}\n"
            )
    except Exception as e:
        text = f"❌ Ulanib bo'lmadi: {e}"
    await message.answer(text, reply_markup=cyber_menu())
    await state.clear()


async def cyber_ua(message: Message, state: FSMContext):
    ua_string = message.text.strip()
    try:
        from user_agents import parse
        ua = parse(ua_string)
        text = (
            f"🤖 <b>User Agent</b>\n\n"
            f"Browser: {ua.browser.family} {ua.browser.version_string}\n"
            f"OS: {ua.os.family} {ua.os.version_string}\n"
            f"Device: {ua.device.family}\n"
            f"Mobile: {'✅' if ua.is_mobile else '❌'}\n"
            f"Tablet: {'✅' if ua.is_tablet else '❌'}\n"
            f"PC: {'✅' if ua.is_pc else '❌'}\n"
            f"Bot: {'✅' if ua.is_bot else '❌'}"
        )
    except ImportError:
        text = f"🤖 <b>User Agent</b>\n\n<code>{ua_string}</code>"
    except Exception as e:
        text = f"❌ Xato: {e}"
    await message.answer(text, reply_markup=cyber_menu())
    await state.clear()


def register(dp: Dispatcher) -> None:
    for cb in CYBER_MAP.keys():
        dp.callback_query.register(cyber_select, F.data == cb)
    dp.message.register(cyber_ip,      CyberStates.ip)
    dp.message.register(cyber_dns,     CyberStates.dns)
    dp.message.register(cyber_whois,   CyberStates.whois)
    dp.message.register(cyber_ssl,     CyberStates.ssl)
    dp.message.register(cyber_headers, CyberStates.headers)
    dp.message.register(cyber_status,  CyberStates.status)
    dp.message.register(cyber_ua,      CyberStates.ua)
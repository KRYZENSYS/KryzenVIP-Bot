"""Utility tools handlers - QR, Base64, Password, JSON, Hash, URL short."""
import base64
import io
import json as jsonlib
import secrets
import string

import qrcode
from aiogram import Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile

from bot.states import ToolStates
from bot.keyboards import tools_menu
from bot.services import get_http
from bot.utils.helpers import sha256, md5


TOOL_MAP = {
    "tool:qr":       (ToolStates.qr,       "🔳 QR Code yaratish uchun matn yuboring:"),
    "tool:base64":   (ToolStates.base64,   "🔤 Encode/decode:\n• encode matn\n• decode base64_string"),
    "tool:json":     (ToolStates.json,     "📋 JSON matn yuboring (format/validate):"),
    "tool:hash":     (ToolStates.hash,     "#️⃣ Hash qilish uchun matn yuboring:"),
    "tool:urlshort": (ToolStates.urlshort, "🔗 Qisqartirish uchun URL yuboring:"),
}


async def tool_select(call: CallbackQuery, state: FSMContext, **kwargs):
    if call.data == "tool:password":
        await generate_password(call)
        return

    config = TOOL_MAP.get(call.data)
    if not config:
        await call.answer("Yangi xususiyat tez orada", show_alert=True)
        return
    s, prompt = config
    await state.set_state(s)
    await call.message.edit_text(
        prompt,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Bekor", callback_data="menu:tools")]
        ])
    )


async def process_qr(message: Message, state: FSMContext):
    text = message.text.strip()
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#b400ff", back_color="#050018")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        await message.answer_photo(
            photo=BufferedInputFile(buf.read(), "qr.png"),
            caption=f"🔳 QR Code:\n<code>{text[:200]}</code>",
            reply_markup=tools_menu()
        )
    except Exception as e:
        await message.answer(f"❌ Xato: {e}")
    await state.clear()


async def process_base64(message: Message, state: FSMContext):
    text = message.text.strip()
    try:
        if text.lower().startswith("encode "):
            actual = text[7:].strip()
            result = base64.b64encode(actual.encode()).decode()
            await message.answer(f"🔤 <b>Encoded:</b>\n\n<code>{result}</code>", reply_markup=tools_menu())
        elif text.lower().startswith("decode "):
            actual = text[7:].strip()
            result = base64.b64decode(actual).decode()
            await message.answer(f"🔤 <b>Decoded:</b>\n\n<code>{result}</code>", reply_markup=tools_menu())
        else:
            try:
                result = base64.b64decode(text).decode()
                await message.answer(f"🔤 <b>Decoded:</b>\n\n<code>{result}</code>", reply_markup=tools_menu())
            except Exception:
                result = base64.b64encode(text.encode()).decode()
                await message.answer(f"🔤 <b>Encoded:</b>\n\n<code>{result}</code>", reply_markup=tools_menu())
    except Exception as e:
        await message.answer(f"❌ Xato: {e}")
    await state.clear()


async def generate_password(call: CallbackQuery):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    pwd = "".join(secrets.choice(alphabet) for _ in range(20))
    text = (
        f"🔑 <b>Yangi parol:</b>\n\n<code>{pwd}</code>\n\n"
        f"📏 Uzunlik: 20\n"
        f"🛡 Xavfsizlik: <b>Juda kuchli</b>\n\n"
        f"⚠️ Boshqa hech kimga ko'rsatmang!"
    )
    await call.message.edit_text(text, reply_markup=tools_menu())


async def process_json(message: Message, state: FSMContext):
    text = message.text.strip()
    try:
        parsed = jsonlib.loads(text)
        pretty = jsonlib.dumps(parsed, indent=2, ensure_ascii=False)
        if len(pretty) > 3500:
            await message.answer_document(
                document=BufferedInputFile(pretty.encode(), "formatted.json"),
                caption="📋 JSON formatlandi"
            )
        else:
            await message.answer(f"📋 <b>Valid JSON:</b>\n\n<pre language=\"json\">{pretty}</pre>", reply_markup=tools_menu())
    except jsonlib.JSONDecodeError as e:
        await message.answer(f"❌ <b>Invalid JSON:</b>\n\n<code>{e}</code>")
    await state.clear()


async def process_hash(message: Message, state: FSMContext):
    import hashlib
    text = message.text
    await message.answer(
        f"#️⃣ <b>Hash natijalari:</b>\n\n"
        f"MD5:    <code>{md5(text)}</code>\n"
        f"SHA1:   <code>{hashlib.sha1(text.encode()).hexdigest()}</code>\n"
        f"SHA256: <code>{sha256(text)}</code>\n"
        f"SHA512: <code>{hashlib.sha512(text.encode()).hexdigest()}</code>",
        reply_markup=tools_menu()
    )
    await state.clear()


async def process_urlshort(message: Message, state: FSMContext):
    url = message.text.strip()
    if not url.startswith(("http://", "https://")):
        await message.answer("❌ URL http:// yoki https:// bilan boshlanishi kerak")
        await state.clear()
        return

    http = get_http()
    if not http:
        await message.answer("❌ HTTP xizmati mavjud emas")
        await state.clear()
        return

    try:
        async with http.get(f"http://tinyurl.com/api-create.php?url={url}") as resp:
            if resp.status == 200:
                short = await resp.text()
                await message.answer(
                    f"🔗 <b>Qisqartirildi:</b>\n\n<code>{short}</code>",
                    reply_markup=tools_menu()
                )
            else:
                await message.answer("❌ Qisqartirib bo'lmadi")
    except Exception as e:
        await message.answer(f"❌ Xato: {e}")
    await state.clear()


def register(dp: Dispatcher) -> None:
    for cb in TOOL_MAP.keys():
        dp.callback_query.register(tool_select, F.data == cb)
    dp.callback_query.register(generate_password, F.data == "tool:password")

    dp.message.register(process_qr,       ToolStates.qr)
    dp.message.register(process_base64,   ToolStates.base64)
    dp.message.register(process_json,     ToolStates.json)
    dp.message.register(process_hash,     ToolStates.hash)
    dp.message.register(process_urlshort, ToolStates.urlshort)
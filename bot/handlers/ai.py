"""AI handlers - 10 features."""
from aiogram import Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger

from bot.database.models import User
from bot.services.ai_service import ai_service
from bot.services.achievements import unlock
from bot.states import AIStates
from bot.keyboards import ai_menu


AI_FEATURES = {
    "ai:chat":          ("💬 AI Chat",          AIStates.chat,          "Savolingizni yozing.",                  "Siz foydali AI assistantsiz. Qisqa va aniq javob bering."),
    "ai:image_prompt":  ("🎨 Image Prompt",     AIStates.image_prompt,  "Tasvir g'oyasini yozing.",              "Siz prompt muhandissiz. Midjourney/DALL-E/Stable Diffusion uchun batafsil prompt yarating."),
    "ai:code":          ("⌨️ Kod yozish",       AIStates.code,          "Nima qilish kerak? Til va talablarni.", "Siz professional dasturchisiz. Toza, samarali, kommentariyali kod yozing."),
    "ai:code_review":   ("🔍 Kod review",       AIStates.code_review,   "Kodni yuboring.",                       "Siz kod reviewchisiz. Bugs, performance, best practices va yaxshilash."),
    "ai:write":         ("📝 Matn",             AIStates.write,         "Mavzu va uslubni yozing.",              "Siz professional muharrirsiz."),
    "ai:translate":     ("🌍 Tarjima",          AIStates.translate,     "Matn: `til: matn` (masalan: `en: Salom`)","Siz tarjimonsiz."),
    "ai:resume":        ("📄 Rezyume",          AIStates.resume,        "Ma'lumotlarni yuboring.",               "Siz HR mutaxassissiz."),
    "ai:ads":           ("📢 Reklama",          AIStates.ads,           "Mahsulot tavsifi va maqsadli auditor.", "Siz reklama copywritersiz."),
    "ai:seo":           ("🔎 SEO Maqola",       AIStates.seo,           "Mavzu va kalit so'zlarni.",             "Siz SEO mutaxassissiz."),
    "ai:prompt_gen":    ("⚡ Prompt gen",       AIStates.prompt_gen,    "Nima kerakligini yozing.",              "Siz prompt muhandissiz."),
}


async def ai_select(call: CallbackQuery, state: FSMContext, **kwargs):
    feature = AI_FEATURES.get(call.data)
    if not feature:
        await call.answer("Unknown feature", show_alert=True)
        return
    title, s, prompt, _ = feature
    await state.set_state(s)
    await call.message.edit_text(
        f"{title}\n\n{prompt}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Bekor", callback_data="menu:ai")]
        ])
    )


async def ai_process(message: Message, state: FSMContext, user: User, session, **kwargs):
    current = await state.get_state()
    if not current:
        return

    # Find feature by state name
    title = "AI"
    system = ""
    text = message.text or ""
    if not text.strip():
        await message.answer("❌ Bo'sh matn")
        return

    for cb, (t, s, _, sys_msg) in AI_FEATURES.items():
        if s.state == current:
            title = t
            system = sys_msg
            break

    # Premium check
    if user.ai_requests_count >= 10 and not user.is_premium:
        await message.answer(
            "💎 <b>AI limiti tugadi!</b>\n\nBepul: 10 so'rov · Premium: cheksiz\n\n/premium",
            reply_markup=ai_menu()
        )
        await state.clear()
        return

    await message.bot.send_chat_action(message.chat.id, "typing")

    if current == AIStates.translate.state:
        parts = text.split(":", 1)
        target_lang = parts[0].strip() if len(parts) > 1 else "en"
        actual_text = parts[1].strip() if len(parts) > 1 else text
        result = await ai_service.translate(actual_text, target_lang)
    elif current == AIStates.code_review.state:
        result = await ai_service.code_review(text)
    else:
        result = await ai_service.chat(text, system)

    user.ai_requests_count = (user.ai_requests_count or 0) + 1
    user.xp = (user.xp or 0) + 5
    user.coins = (user.coins or 0) + 1

    await message.answer(f"{title}\n\n{result}", reply_markup=ai_menu())
    await unlock(session, user, "FIRST_CHAT")
    await state.clear()


def register(dp: Dispatcher) -> None:
    for cb in AI_FEATURES.keys():
        dp.callback_query.register(ai_select, F.data == cb)
    dp.message.register(ai_process, *AIStates.__states__)
"""AI service - OpenAI wrapper + fallback."""
from typing import Optional
from loguru import logger

from bot.config import settings


class AIService:
    def __init__(self) -> None:
        self.client = None
        if settings.OPENAI_API_KEY:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.success("OpenAI client initialized")
            except Exception as e:
                logger.warning(f"OpenAI init failed: {e}")

    async def chat(self, prompt: str, system: str = "") -> str:
        if self.client:
            return await self._openai_chat(prompt, system)
        return self._smart_fallback(prompt, system, mode="chat")

    async def translate(self, text: str, target_lang: str) -> str:
        system = f"You are a translator. Translate to {target_lang}. Only output the translation, no comments."
        if self.client:
            return await self._openai_chat(text, system, max_tokens=2000)
        return f"[Tarjima ({target_lang})]: {text}"

    async def code_review(self, code: str) -> str:
        system = "You are a senior code reviewer. Provide detailed review with bugs, performance issues, best practices, and improvements. Be concise but thorough."
        if self.client:
            return await self._openai_chat(code, system, max_tokens=2000)
        return self._smart_fallback(code, system, mode="code")

    async def _openai_chat(self, prompt: str, system: str = "", max_tokens: int = 1000) -> str:
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return self._smart_fallback(prompt, system)

    def _smart_fallback(self, prompt: str, system: str = "", mode: str = "chat") -> str:
        """Smart fallback responses when API is unavailable."""
        prompts = {
            "chat": f"💬 Sizning savolingiz: {prompt[:200]}\n\n🤖 OpenAI API kaliti o'rnatilmagan yoki ishlamayapti.\n\n.env faylida OPENAI_API_KEY ni sozlang.",
            "code": f"⌨️ Kod tahlili:\n\n⚠️ OpenAI API mavjud emas.\n\nKod:\n{code[:500] if 'code' in prompt else prompt[:300]}",
            "translate": f"🌍 Tarjima: {prompt[:200]}\n\n⚠️ Tarjimon xizmati vaqtincha mavjud emas.",
        }
        return prompts.get(mode, prompts["chat"])


# Module-level singleton instance
ai_service = AIService()
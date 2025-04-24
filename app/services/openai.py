from openai import AsyncOpenAI
from app.settings import settings


class OpenAIService:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model

    async def generate_name(self) -> str:
        prompt = "Придумай реалистичное имя и фамилию для пользователя Telegram."
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
                max_tokens=20,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[OpenAI] Ошибка генерации имени: {e}")
            return "Ошибка генерации имени"

    async def generate_comment(self, tone: str = "neutral", custom_prompt: str = None) -> str:
        if custom_prompt:
            prompt = custom_prompt
        else:
            tone_prompts = {
                "positive": "Напиши короткий положительный комментарий на русском языке для Telegram-поста, выражающий одобрение или поддержку.",
                "neutral": "Напиши короткий нейтральный комментарий на русском языке, без явной эмоциональной окраски, подходящий под Telegram-пост.",
                "question": "Напиши короткий вопросительный комментарий на русском языке, который мог бы быть задан в ответ на Telegram-пост.",
                "critical": "Напиши короткий критический комментарий на русском языке, но без агрессии, адекватный под Telegram-пост.",
            }
            prompt = tone_prompts.get(tone, tone_prompts["neutral"])

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
                max_tokens=60,
                temperature=0.9,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[OpenAI] Ошибка генерации комментария: {e}")
            return "Ошибка генерации комментария"
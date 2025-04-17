from openai import AsyncOpenAI
from settings import settings


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

    async def generate_comment(self, prompt: str = None) -> str:
        if not prompt:
            prompt = (
                "Напиши короткий, реалистичный комментарий, который мог бы оставить обычный пользователь "
                "в Telegram-канале под постом."
            )
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

    async def generate_avatar(self) -> str:
        prompt = (
            "Сгенерируй портрет обычного человека (нейтральный фон, свет, прямой взгляд), "
            "без текста, логотипов или лишних элементов. Используется для профиля Telegram."
        )
        try:
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024",
            )
            return response.data[0].url
        except Exception as e:
            print(f"[OpenAI] Ошибка генерации аватара: {e}")
            return ""
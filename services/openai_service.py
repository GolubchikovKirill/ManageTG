import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-3.5-turbo"  # рекомендуется для генерации

    async def generate_name(self) -> str:
        prompt = "Придумай правдоподобное имя для пользователя Telegram."
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": prompt}],
            max_tokens=10,
            temperature=0.8,
        )
        return response.choices[0].message.content.strip()

    async def generate_comment(self) -> str:
        prompt = (
            "Придумай реалистичный комментарий, который пользователь мог бы оставить в Telegram-группе."
        )
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": prompt}],
            max_tokens=50,
            temperature=0.9,
        )
        return response.choices[0].message.content.strip()
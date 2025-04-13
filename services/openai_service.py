import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-3.5-turbo"

    async def generate_name(self) -> str:
        prompt = "Придумай правдоподобное имя для пользователя Telegram."
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
                max_tokens=10,
                temperature=0.8,
            )
            print(response)  # Логирование ответа от OpenAI
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in generate_name: {e}")
            raise

    async def generate_comment(self) -> str:
        prompt = (
            "Придумай реалистичный не большой комментарий, который пользователь мог бы оставить в Telegram-группе."
        )
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
                max_tokens=50,
                temperature=0.9,
            )
            print(response)  # Логирование ответа от OpenAI
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in generate_comment: {e}")
            raise
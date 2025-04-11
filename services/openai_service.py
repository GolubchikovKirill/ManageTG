import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

class OpenAIService:
    def __init__(self):
        self.model = "text-davinci-003"

    def generate_name(self) -> str:
        prompt = "Generate a random name for a Telegram user."
        response = openai.Completion.create(
            engine=self.model,
            prompt=prompt,
            max_tokens=10
        )
        return response.choices[0].text.strip()

    def generate_comment(self) -> str:
        prompt = "Generate a random comment that looks like something a real user would write in a Telegram group."
        response = openai.Completion.create(
            engine=self.model,
            prompt=prompt,
            max_tokens=50
        )
        return response.choices[0].text.strip()
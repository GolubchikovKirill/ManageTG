import os
import random
import asyncio
from pyrogram import Client
from sqlalchemy.orm import Session
from database.models import Actions, Channels
from services.openai_service import OpenAIService


class BotActionExecutor:
    def __init__(self, session: Session, openai_service: OpenAIService, session_folder: str = "sessions"):
        self.session = session
        self.openai_service = openai_service
        self.session_folder = session_folder

    @staticmethod
    def random_time_with_spread(time_frame: int, spread_percent: int) -> int:
        """
        Генерация случайного времени с учетом разброса.
        Например, если time_frame = 1 час, spread_percent = 20%,
        то результат будет в пределах 48-72 минут.
        """
        spread = time_frame * spread_percent / 100
        random_minutes = random.randint(
            int((time_frame - spread) * 60),
            int((time_frame + spread) * 60)
        )
        return random_minutes

    async def execute_action(self, action: Actions, bot_client: Client):
        """
        Выполнение действия (комментарий, реакция, просмотр) для бота.
        """
        delay_minutes = self.random_time_with_spread(action.action_time, action.random_percentage)
        await asyncio.sleep(delay_minutes * 60)  # Задержка перед действием (в секундах)

        if action.action_type == "comment":
            await self.execute_comment(action.channel_id, action.count, bot_client)
        elif action.action_type == "reaction":
            await self.execute_reaction(action.channel_id, action.count, bot_client)
        elif action.action_type == "view":
            await self.execute_view(action.channel_id, action.count, bot_client)

    async def execute_comment(self, channel_id: int, count: int, bot_client: Client):
        channel = self.session.query(Channels).filter(Channels.id == channel_id).first()
        if not channel:
            return

        comment = await self.openai_service.generate_comment(channel.comment)
        for _ in range(count):
            await bot_client.send_message(channel.name, comment)

    async def execute_reaction(self, channel_id: int, count: int, bot_client: Client):
        channel = self.session.query(Channels).filter(Channels.id == channel_id).first()
        if not channel:
            return

        reactions = ["❤️", "👍", "👎", "🎭"]
        for _ in range(count):
            reaction = random.choice(reactions)
            await bot_client.send_reaction(channel.name, reaction)

    async def execute_view(self, channel_id: int, count: int, bot_client: Client):
        channel = self.session.query(Channels).filter(Channels.id == channel_id).first()
        if not channel:
            return

        for _ in range(count):
            await bot_client.send_message(channel.name, "Просмотрено!")  # заменяется имитацией

    def load_sessions(self):
        sessions = []
        for filename in os.listdir(self.session_folder):
            if filename.endswith(".session"):
                session_name = filename[:-8]
                sessions.append(session_name)
        return sessions

    async def run(self, action: Actions, api_id: str, api_hash: str):
        sessions = self.load_sessions()
        for session_name in sessions:
            bot_client = Client(session_name=session_name, api_id=api_id, api_hash=api_hash)
            await bot_client.start()

            await self.execute_action(action, bot_client)

            await bot_client.stop()
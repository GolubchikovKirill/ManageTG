import os
import random
import asyncio
from pyrogram import Client, errors
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Actions, Channels
from services.openai_service import OpenAIService


class BotActionExecutor:
    def __init__(self, session: AsyncSession, openai_service: OpenAIService, session_folder: str = "sessions"):
        self.session = session
        self.openai_service = openai_service
        self.session_folder = session_folder

    @staticmethod
    def random_time_with_spread(time_frame: int, spread_percent: int) -> int:
        spread = time_frame * spread_percent / 100
        return random.randint(
            int((time_frame - spread) * 60),
            int((time_frame + spread) * 60)
        )

    async def execute_action(self, action: Actions, bot_client: Client):
        try:
            delay_minutes = self.random_time_with_spread(action.action_time, action.random_percentage)
            await asyncio.sleep(delay_minutes)

            if action.action_type == "comment":
                await self.execute_comment(action.channel_id, action.count, bot_client)
            elif action.action_type == "reaction":
                await self.execute_reaction(action.channel_id, action.count, bot_client)
            elif action.action_type == "view":
                await self.execute_view(action.channel_id, action.count, bot_client)
        except errors.FloodWait as e:
            print(f"FloodWait error: {e}")
        except Exception as e:
            print(f"Error executing action: {e}")

    async def get_channel(self, channel_id: int) -> Channels | None:
        result = await self.session.execute(
            select(Channels).where(Channels.id == channel_id)
        )
        return result.scalars().first()

    async def execute_comment(self, channel_id: int, count: int, bot_client: Client):
        channel = await self.get_channel(channel_id)
        if not channel:
            print(f"Channel {channel_id} not found.")
            return

        try:
            # Подписываемся на канал
            print(f"Trying to join channel {channel.name}...")
            await bot_client.join_chat(channel.name)
            print(f"Successfully joined channel: {channel.name}")

            # Получаем последний пост в канале
            async for message in bot_client.get_chat_history(channel.name, limit=1):
                print(f"Last message found: {message.message_id}")

                # Проверяем, что это канал
                if message.chat.type in ['supergroup', 'channel']:
                    for _ in range(count):
                        comment = await self.openai_service.generate_comment(channel.comment)
                        print(f"Generated comment: {comment}")

                        # Отправляем комментарий под этим постом
                        await bot_client.send_message(
                            chat_id=message.chat.id,
                            text=comment,
                            reply_to_message_id=message.message_id  # Комментируем под последним постом
                        )
                    print(f"Comment(s) sent under the post with message_id: {message.message_id}")
                    break  # Завершаем после первого поста

        except errors.FloodWait as e:
            print(f"FloodWait error: {e}")
        except Exception as e:
            print(f"Error sending comment: {e}")

    async def execute_reaction(self, channel_id: int, count: int, bot_client: Client):
        channel = await self.get_channel(channel_id)
        if not channel:
            print(f"Channel {channel_id} not found.")
            return

        try:
            reactions = ["❤️", "👍", "👎", "🎭"]
            for _ in range(count):
                await bot_client.send_reaction(channel.name, random.choice(reactions))
        except Exception as e:
            print(f"Error sending reaction: {e}")

    async def execute_view(self, channel_id: int, count: int, bot_client: Client):
        channel = await self.get_channel(channel_id)
        if not channel:
            print(f"Channel {channel_id} not found.")
            return

        try:
            for _ in range(count):
                await bot_client.send_message(channel.name, "Просмотрено!")  # имитация
        except Exception as e:
            print(f"Error sending view: {e}")

    def load_sessions(self):
        if not os.path.exists(self.session_folder):
            print(f"Session folder '{self.session_folder}' not found.")
            return []

        return [
            filename[:-8]
            for filename in os.listdir(self.session_folder)
            if filename.endswith(".session")
        ]

    async def run(self, action: Actions, api_id: str, api_hash: str):
        sessions = self.load_sessions()
        tasks = []

        for session_name in sessions:
            session_path = os.path.join(self.session_folder, session_name)

            # Убедимся, что сессии создаются в указанной папке
            if not os.path.exists(self.session_folder):
                os.makedirs(self.session_folder)

            async def run_for_client(path=session_path):
                async with Client(path, api_id=api_id, api_hash=api_hash) as bot_client:
                    await self.execute_action(action, bot_client)

            tasks.append(asyncio.create_task(run_for_client()))

        await asyncio.gather(*tasks)

        return {"message": "Actions executed successfully"}
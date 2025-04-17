import asyncio
import os
import random
from pyrogram import Client, errors
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Actions, Channels
from services.openai_service import OpenAIService


class BotActionExecutor:
    def __init__(self, session: AsyncSession, openai_service: OpenAIService, session_folder: str = "sessions"):
        self.session = session
        self.openai_service = openai_service
        self.session_folder = session_folder

    @staticmethod
    def random_time_with_spread(base_minutes: int, spread_percent: int) -> int:
        spread = base_minutes * spread_percent / 100
        return random.randint(int((base_minutes - spread) * 60), int((base_minutes + spread) * 60))

    async def get_channel(self, channel_id: int) -> Channels | None:
        result = await self.session.execute(select(Channels).where(Channels.id == channel_id))
        return result.scalars().first()

    async def execute_action(self, action: Actions, bot_client: Client):
        try:
            delay = self.random_time_with_spread(action.action_time, action.random_percentage)
            print(f"⌛ Ждём {delay // 60} мин перед выполнением действия...")
            await asyncio.sleep(delay)

            if action.action_type == "comment":
                await self.execute_comment(action.channel_id, action.count, bot_client)
            elif action.action_type == "reaction":
                await self.execute_reaction(action.channel_id, action.count, bot_client)
            elif action.action_type == "view":
                await self.execute_view(action.channel_id, action.count, bot_client)
        except errors.FloodWait as e:
            print(f"[Telegram] FloodWait: ждём {e.value} секунд")
            await asyncio.sleep(e.value)
        except Exception as e:
            print(f"[Executor] Ошибка выполнения действия: {type(e).__name__}: {e}")

    async def execute_comment(self, channel_id: int, count: int, bot_client: Client):
        channel = await self.get_channel(channel_id)
        if not channel:
            print(f"[Comment] Канал с ID {channel_id} не найден.")
            return

        try:
            chat = await bot_client.get_chat(channel.name)
            if not chat.linked_chat:
                print("[Comment] У канала нет обсуждений.")
                return

            discussion = await bot_client.get_chat(chat.linked_chat.id)

            # Проверка участия в чате
            try:
                await bot_client.get_chat_member(discussion.id, "me")
            except errors.UserNotParticipant:
                print("[Comment] Бот не состоит в обсуждении. Присоединяемся...")
                await bot_client.join_chat(discussion.username or discussion.id)
                await asyncio.sleep(3)

            # Проверка прав
            member = await bot_client.get_chat_member(discussion.id, "me")
            if member.status != "administrator" and (not discussion.permissions or not discussion.permissions.can_send_messages):
                print("[Comment] Нет прав на отправку сообщений.")
                return

            # Получаем последние 3 поста
            posts = []
            async for msg in bot_client.get_chat_history(chat.id, limit=10):
                if not msg.service and (msg.text or msg.caption):
                    posts.append(msg)
                    if len(posts) == 3:
                        break

            if not posts:
                print("[Comment] Нет подходящих постов.")
                return

            per_post = max(1, count // len(posts))
            total_sent = 0

            for post in posts:
                for _ in range(per_post):
                    comment = await self.openai_service.generate_comment()
                    await bot_client.send_message(
                        discussion.id,
                        comment,
                        reply_to_message_id=post.id
                    )
                    total_sent += 1
                    await asyncio.sleep(random.randint(10, 25))

            print(f"[Comment] Всего отправлено комментариев: {total_sent}/{count}")

        except Exception as e:
            print(f"[Comment] Ошибка: {type(e).__name__}: {e}")

    async def execute_view(self, channel_id: int, count: int, bot_client: Client):
        channel = await self.get_channel(channel_id)
        if not channel:
            print(f"[View] Канал с ID {channel_id} не найден.")
            return

        viewed = 0
        try:
            async for msg in bot_client.get_chat_history(channel.name, limit=100):
                if msg.photo or msg.video:
                    try:
                        await bot_client.download_media(msg, file_name=os.devnull)
                        viewed += 1
                    except Exception as e:
                        print(f"[View] Ошибка загрузки медиа: {e}")
                await asyncio.sleep(random.uniform(0.5, 2.0))
                if viewed >= count:
                    break

            print(f"[View] Просмотрено: {viewed}/{count}")

        except Exception as e:
            print(f"[View] Ошибка получения истории: {e}")

    def load_sessions(self) -> list[str]:
        if not os.path.exists(self.session_folder):
            os.makedirs(self.session_folder, exist_ok=True)
            return []

        return [
            f.rsplit(".", 1)[0]
            for f in os.listdir(self.session_folder)
            if f.endswith(".session")
        ]

    async def run(self, action: Actions, api_id: str, api_hash: str):
        sessions = self.load_sessions()
        tasks = []

        for session_name in sessions:
            async def session_task(name=session_name):
                try:
                    async with Client(
                        name=name,
                        api_id=api_id,
                        api_hash=api_hash,
                        workdir=self.session_folder
                    ) as client:
                        await self.execute_action(action, client)
                except Exception as e:
                    print(f"[Runner] Ошибка в сессии {name}: {e}")

            tasks.append(asyncio.create_task(session_task()))

        await asyncio.gather(*tasks, return_exceptions=True)
        return {"status": "completed", "sessions_processed": len(sessions)}
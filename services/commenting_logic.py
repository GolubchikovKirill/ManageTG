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

    @staticmethod
    async def _join_channel_if_needed(bot_client: Client, channel_username_or_id: str):
        try:
            await bot_client.get_chat_member(channel_username_or_id, "me")
        except errors.UserNotParticipant:
            print(f"[Join] Бот не подписан на {channel_username_or_id}. Присоединяемся...")
            await bot_client.join_chat(channel_username_or_id)
            await asyncio.sleep(3)

    async def execute_comment(self, action: Actions, bot_client: Client):
        channel = await self.get_channel(action.channel_id)
        if not channel:
            print(f"[Comment] Канал с ID {action.channel_id} не найден.")
            return

        try:
            await self._join_channel_if_needed(bot_client, channel.name)

            chat = await bot_client.get_chat(channel.name)
            if not chat.linked_chat:
                print("[Comment] У канала нет чата обсуждений.")
                return

            discussion = await bot_client.get_chat(chat.linked_chat.id)

            try:
                await bot_client.get_chat_member(discussion.id, "me")
            except errors.UserNotParticipant:
                print("[Comment] Бот не состоит в чате обсуждений. Присоединяемся...")
                await bot_client.join_chat(discussion.username or discussion.id)
                await asyncio.sleep(3)

            member = await bot_client.get_chat_member(discussion.id, "me")
            if member.status != "administrator" and (not discussion.permissions or not discussion.permissions.can_send_messages):
                print("[Comment] Нет прав на отправку сообщений.")
                return

            posts = []
            async for msg in bot_client.get_chat_history(chat.id, limit=10):
                if not msg.service and (msg.text or msg.caption):
                    posts.append(msg)
                    if len(posts) == 3:
                        break

            if not posts:
                print("[Comment] Нет подходящих постов.")
                return

            total_sent = 0
            types = [
                ("positive_count", "positive"),
                ("negative_count", "negative"),
                ("critical_count", "critical"),
                ("question_count", "question"),
            ]

            for attr, tone in types:
                count = getattr(action, attr, 0) or 0
                if count <= 0:
                    continue

                per_post = max(1, count // len(posts))
                for post in posts:
                    for _ in range(per_post):
                        prompt = action.custom_prompt if action.custom_prompt else None
                        comment = await self.openai_service.generate_comment(
                            tone=tone,
                            custom_prompt=prompt or (post.text or post.caption)
                        )
                        await bot_client.send_message(
                            discussion.id,
                            comment,
                            reply_to_message_id=post.id
                        )
                        total_sent += 1
                        await asyncio.sleep(random.randint(10, 25))

            print(f"[Comment] Всего отправлено комментариев: {total_sent}")

        except Exception as e:
            print(f"[Comment] Ошибка: {type(e).__name__}: {e}")

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
                        delay = self.random_time_with_spread(action.action_time, action.random_percentage)
                        print(f"⌛ Ждём {delay // 60} мин перед выполнением действия...")
                        await asyncio.sleep(delay)

                        if action.action_type == "comment":
                            await self.execute_comment(action, client)
                except Exception as e:
                    print(f"[Runner] Ошибка в сессии {name}: {e}")

            tasks.append(asyncio.create_task(session_task()))

        await asyncio.gather(*tasks, return_exceptions=True)
        return {"status": "completed", "sessions_processed": len(sessions)}
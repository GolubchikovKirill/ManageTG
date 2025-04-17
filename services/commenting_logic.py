import asyncio
import os
import random
from datetime import timedelta, datetime

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

    @staticmethod
    async def _join_channel_if_needed(bot_client: Client, channel_username_or_id: str):
        try:
            await bot_client.get_chat_member(channel_username_or_id, "me")
        except errors.UserNotParticipant:
            print(f"[Join] Бот не подписан на {channel_username_or_id}. Присоединяемся...")
            await bot_client.join_chat(channel_username_or_id)
            await asyncio.sleep(3)

    async def execute_comment(self, channel_id: int, count: int, bot_client: Client):
        channel = await self.get_channel(channel_id)
        if not channel:
            print(f"[Comment] Канал с ID {channel_id} не найден.")
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

        await self._join_channel_if_needed(bot_client, channel.name)

        viewed = 0
        try:
            async for msg in bot_client.get_chat_history(channel.name, limit=50):
                if any([msg.text, msg.photo, msg.video, msg.document, msg.web_page]):
                    try:
                        await bot_client.get_messages(channel.name, msg.id)
                        viewed += 1
                    except Exception as e:
                        print(f"[View] Ошибка симуляции просмотра: {e}")

                    await asyncio.sleep(random.uniform(0.8, 2.0))
                    if viewed >= count:
                        break

            print(f"[View] Просмотрено: {viewed}/{count}")

        except Exception as e:
            print(f"[View] Ошибка получения истории: {e}")

    async def execute_reaction(self, channel_id: int, count: int, bot_client: Client):
        channel = await self.get_channel(channel_id)
        if not channel:
            print(f"[Reaction] Channel {channel_id} not found")
            return

        try:
            # Присоединяемся к каналу
            try:
                await bot_client.join_chat(channel.name)
                await asyncio.sleep(3)
            except Exception as join_error:
                print(f"[Reaction] Join error: {join_error}")
                return

            # Получаем актуальные настройки реакций
            allowed_reactions = await self._get_allowed_reactions(bot_client, channel.name)
            if not allowed_reactions:
                print("[Reaction] No allowed reactions in this channel")
                return

            # Собираем сообщения с возможностью реакций
            posts = await self._collect_reactable_messages(bot_client, channel.name)
            if not posts:
                print("[Reaction] No suitable messages found")
                return

            # Ставим реакции
            success_count = 0
            for post in posts:
                if success_count >= count:
                    break
                try:
                    reaction = random.choice(allowed_reactions)
                    await self._send_safe_reaction(bot_client, post, reaction)
                    success_count += 1
                    await asyncio.sleep(random.uniform(5, 15))
                except Exception as e:
                    print(f"[Reaction] Error: {type(e).__name__}")

            print(f"[Reaction] Success: {success_count}/{count} reactions")

        except Exception as main_error:
            print(f"[Reaction] Critical error: {main_error}")

    @staticmethod
    async def _get_allowed_reactions(client: Client, chat_id: str) -> list:
        try:
            chat = await client.get_chat(chat_id)
            if not chat.available_reactions:
                return []

            return [reaction.emoji for reaction in chat.available_reactions
                    if not reaction.is_premium]
        except Exception as e:
            print(f"[Reaction] Can't get reactions: {e}")
            return ["👍", "❤", "🔥", "🎉"]  # Fallback

    async def _collect_reactable_messages(self, client: Client, chat_id: str) -> list:
        posts = []
        try:
            async for msg in client.get_chat_history(chat_id, limit=50):
                if self._is_message_reactable(msg):
                    posts.append(msg)
                if len(posts) >= 20:
                    break
        except Exception as e:
            print(f"[Reaction] History error: {e}")
        return posts

    @staticmethod
    def _is_message_reactable(msg) -> bool:
        return (
                not msg.service and
                not msg.forward_from and
                msg.date > datetime.now() - timedelta(hours=48)
        )

    @staticmethod
    async def _send_safe_reaction(client: Client, post, reaction: str):
        try:
            await client.send_reaction(
                chat_id=post.chat.id,
                message_id=post.id,
                emoji=reaction
            )
            print(f"[Reaction] {reaction} → {post.id}")
        except errors.ReactionInvalid:
            print(f"[Reaction] Invalid reaction: {reaction}")
        except errors.FloodWait as e:
            print(f"[Reaction] Flood wait: {e.value}s")
            await asyncio.sleep(e.value)
        except errors.MsgIdInvalid:
            print(f"[Reaction] Invalid message ID: {post.id}")

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
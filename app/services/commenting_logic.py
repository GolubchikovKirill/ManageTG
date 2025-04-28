import asyncio
import os
import random
from pyrogram import Client, errors
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import CommentActions, Channels
from app.services.openai import OpenAIService


class BotActionExecutor:
    def __init__(self, session: AsyncSession, openai_service: OpenAIService, session_folder: str = "sessions"):
        self.session = session
        self.openai_service = openai_service
        self.session_folder = session_folder

    @staticmethod
    def random_time_with_spread(base_seconds: int, spread_percent: int) -> int:
        spread = base_seconds * spread_percent / 100
        return random.randint(int(base_seconds - spread), int(base_seconds + spread))

    async def get_channel(self, channel_id: int) -> Channels | None:
        result = await self.session.execute(select(Channels).where(Channels.id == channel_id))
        return result.scalars().first()

    @staticmethod
    async def _join_channel_if_needed(client: Client, channel_username: str):
        try:
            await client.get_chat_member(channel_username, "me")
        except errors.UserNotParticipant:
            print(f"[Join] Присоединение к каналу {channel_username}")
            await client.join_chat(channel_username)
            await asyncio.sleep(3)

    async def execute_comment(
            self,
            action: CommentActions,
            client: Client,
            count: int,
            custom_prompt: str | None = None,
            action_type: str | None = None
    ):
        try:
            channel = await self.get_channel(action.channel_id)
            if not channel:
                print(f"[ERROR] Канал {action.channel_id} не найден")
                return

            await self._join_channel_if_needed(client, channel.name)
            main_chat = await client.get_chat(channel.name)

            if not main_chat.linked_chat:
                print(f"[ERROR] Нет чата обсуждений для {channel.name}")
                return

            discussion = await client.get_chat(main_chat.linked_chat.id)

            # Сбор только оригинальных постов
            posts = []
            async for msg in client.get_chat_history(main_chat.id, limit=15):
                if not msg.service and not msg.reply_to_message_id:
                    post_content = await self._process_post_content(msg)
                    if post_content:
                        posts.append((msg, post_content))
                        print(f"[DEBUG] Найден пост ID {msg.id}: {post_content[:50]}...")

            print(f"[INFO] Найдено оригинальных постов: {len(posts)}")

            total_sent = 0
            comment_types = self._get_comment_types(action_type)

            for tone in comment_types:
                target_count = getattr(action, f"{tone}_count", 0)
                if target_count <= 0:
                    continue

                print(f"[PROCESS] Обработка комментариев типа '{tone}'")

                for post, post_content in posts:
                    if total_sent >= count:
                        return

                    try:
                        comment = await self.openai_service.generate_comment(tone, post_content)
                        if comment:
                            await self._send_comment(client, discussion.id, post.id, comment)
                            total_sent += 1
                            print(f"[SENT] Комментарий к посту {post.id}: {comment}")
                            await self._delay(action)

                    except errors.FloodWait as e:
                        print(f"[FLOOD] Ожидание {e.value} сек")
                        await asyncio.sleep(e.value)
                    except Exception as e:
                        print(f"[ERROR] Ошибка: {str(e)}")

            print(f"[RESULT] Успешно отправлено {total_sent}/{count} комментариев")

        except Exception as e:
            print(f"[CRITICAL] Критическая ошибка: {str(e)}")

    async def _process_post_content(self, post) -> str:
        """Получение и обработка контента поста"""
        if post.text:
            return post.text.strip()
        if post.caption:
            return post.caption.strip()
        return self._describe_media(post)

    @staticmethod
    def _describe_media(post) -> str:
        """Генерация описания для медиа-контента"""
        media_types = {
            'photo': 'Фото',
            'video': 'Видео',
            'document': 'Документ',
            'audio': 'Аудио'
        }
        for media_type, desc in media_types.items():
            if getattr(post, media_type, None):
                return f"{desc} контент: {post.caption}" if post.caption else desc
        return "Медиа-пост"

    @staticmethod
    async def _send_comment(client: Client, chat_id: int, post_id: int, comment: str):
        """Отправка комментария под оригинальным постом"""
        try:
            await client.send_message(
                chat_id=chat_id,
                text=comment,
                reply_to_message_id=post_id  # Ответ именно на пост, а не комментарий
            )
        except Exception as e:
            print(f"[SEND ERROR] Ошибка отправки: {str(e)}")
            raise

    @staticmethod
    def _get_comment_types(action_type: str | None) -> list:
        """Определение типов комментариев для обработки"""
        if action_type:
            return [action_type]
        return ["positive", "neutral", "critical", "question"]

    async def _delay(self, action: CommentActions):
        """Естественная задержка между отправками"""
        delay = self.random_time_with_spread(
            base_seconds=action.action_time * 60,
            spread_percent=action.random_percentage
        )
        print(f"[DELAY] Задержка {delay} сек")
        await asyncio.sleep(delay)

    def load_sessions(self) -> list[str]:
        """Загрузка доступных сессий"""
        if not os.path.exists(self.session_folder):
            return []
        return [f.split(".")[0] for f in os.listdir(self.session_folder) if f.endswith(".session")]

    async def run(self, action: CommentActions, api_id: str, api_hash: str, count: int,
                  custom_prompt: str | None = None, action_type: str | None = None):
        """Запуск процесса комментирования"""
        sessions = self.load_sessions()
        if not sessions:
            print("[ERROR] Нет доступных сессий")
            return

        tasks = [self._create_task(s, api_id, api_hash, action, count, custom_prompt, action_type)
                 for s in sessions]
        await asyncio.gather(*tasks)

    def _create_task(self, session_name: str, api_id: str, api_hash: str,
                     action: CommentActions, count: int, custom_prompt: str | None,
                     action_type: str | None):
        """Создание асинхронной задачи"""

        async def task():
            try:
                async with Client(
                        name=session_name,
                        api_id=api_id,
                        api_hash=api_hash,
                        workdir=self.session_folder
                ) as client:
                    print(f"\n[SESSION] Запуск сессии {session_name}")
                    await self.execute_comment(action, client, count, custom_prompt, action_type)
            except Exception as e:
                print(f"[SESSION ERROR] {session_name}: {str(e)}")

        return task()
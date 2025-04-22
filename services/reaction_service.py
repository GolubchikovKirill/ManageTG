import asyncio
import os
import random
from pyrogram import Client


class ReactionService:
    def __init__(self, sessions_path: str = "sessions"):
        self.session_folder = sessions_path

    async def _send_reaction(self, session_name: str, chat_id: int, message_id: int, emoji: str):
        try:
            async with Client(session_name, workdir=self.session_folder) as app:
                await app.send_reaction(chat_id=chat_id, message_id=message_id, emoji=emoji)
        except Exception as e:
            print(f"[ReactionService] Ошибка реакции ({session_name}): {e}")

    async def get_post_comments(self, channel_id: str, post_count: int = 3):
        # Получаем последние сообщения
        async with Client("bot", workdir=self.session_folder) as app:
            messages = await app.get_chat_history(channel_id, limit=post_count)

        # Извлекаем комментарии для каждого поста
        comments = []
        for message in messages:
            if message.replies:  # Проверка на наличие комментариев
                async for reply in app.get_chat_replies(channel_id, message_id=message.message_id):
                    comments.append(reply.text)

        return comments

    async def react_to_last_posts(self, channel_id: str, emoji: str = "❤️", max_sessions: int = 10,
                                  post_count: int = 3):
        # Получаем последние сообщения
        async with Client("bot", workdir=self.session_folder) as app:
            messages = await app.get_chat_history(channel_id, limit=post_count)

        # Выбираем только последние post_count сообщений
        tasks = []
        session_dirs = [f for f in os.listdir(self.session_folder) if
                        os.path.isdir(os.path.join(self.session_folder, f))]
        random.shuffle(session_dirs)
        session_dirs = session_dirs[:max_sessions]

        for message in messages:
            chat_id = message.chat.id
            message_id = message.message_id

            # Получаем комментарии к посту
            comments = await self.get_post_comments(channel_id, post_count=post_count)
            print(f"Комментарии к посту {message_id}: {comments}")

            # Отправляем реакции
            for session_name in session_dirs:
                tasks.append(self._send_reaction(session_name, chat_id, message_id, emoji))

        await asyncio.gather(*tasks)

    def load_sessions(self) -> list[str]:
        if not os.path.exists(self.session_folder):
            os.makedirs(self.session_folder, exist_ok=True)
            return []

        return [
            f.rsplit(".", 1)[0]
            for f in os.listdir(self.session_folder)
            if f.endswith(".session")
        ]

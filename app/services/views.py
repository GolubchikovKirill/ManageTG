from pyrogram import Client
from pyrogram.raw.functions.messages import GetMessagesViews
import asyncio
import random
import os


class ViewService:
    def __init__(self, sessions_path: str, action_time: int, random_percentage: int = 20):
        self.sessions_path = sessions_path
        self.action_time = action_time
        self.random_percentage = random_percentage

    @staticmethod
    def random_time_with_spread(base_seconds: int, spread_percent: int) -> int:
        spread = base_seconds * spread_percent / 100
        return random.randint(int(base_seconds - spread), int(base_seconds + spread))

    async def _send_view(self, session_name: str, chat: str, message_id: int):
        try:
            async with Client(session_name, workdir=self.sessions_path) as app:
                peer = await app.resolve_peer(chat)  # Получаем RAW-представление чата

                await app.invoke(
                    GetMessagesViews(
                        peer=peer,
                        id=[message_id],  # список сообщений
                        increment=True    # Увеличиваем просмотры
                    )
                )

                print(f"[ViewService] ✅ Просмотр отправлен от {session_name}")
        except Exception as e:
            print(f"[ViewService] ⚠️ Ошибка просмотра ({session_name}): {e}")

    async def add_views(self, chat: str, session_limit: int, delay_between: int = 10):
        session_dirs = [f for f in os.listdir(self.sessions_path) if os.path.isdir(os.path.join(self.sessions_path, f))]
        random.shuffle(session_dirs)
        session_dirs = session_dirs[:session_limit]

        print(f"[ViewService] Старт накрутки просмотров на посты канала: {chat}")
        print(f"[ViewService] Количество выбранных аккаунтов: {len(session_dirs)}")

        tasks = []
        async with Client("bot", workdir=self.sessions_path) as app:
            messages = await app.get_chat_history(chat, limit=10)

        for message in messages:
            print(f"[ViewService] Обрабатываем пост {message.message_id}")
            for session_name in session_dirs:
                tasks.append(asyncio.create_task(self._send_view(session_name, chat, message.message_id)))

                delay = self.random_time_with_spread(delay_between, self.random_percentage)
                print(f"[ViewService] Пауза {delay} секунд перед следующим аккаунтом...")
                await asyncio.sleep(delay)

        await asyncio.gather(*tasks)

        total_duration = self.action_time * 60
        print(f"[ViewService] Завершение через {total_duration // 60} минут ожидания...")
        await asyncio.sleep(total_duration)
from pyrogram import Client
import asyncio
import os
import random

class ViewService:
    def __init__(self, sessions_path: str, action_time: int, random_percentage: int = 20):
        self.sessions_path = sessions_path
        self.action_time = action_time
        self.random_percentage = random_percentage

    @staticmethod
    def random_time_with_spread(base_minutes: int, spread_percent: int) -> int:
        spread = base_minutes * spread_percent / 100
        return random.randint(int((base_minutes - spread) * 60), int((base_minutes + spread) * 60))

    async def _send_view(self, session_name: str, post_link: str):
        try:
            async with Client(session_name, workdir=self.sessions_path) as app:
                # Выполняем действие (например, "typing") в чате
                await app.invoke_chat_action(chat_id=post_link.split('/')[-2], action="typing")
                # Просматриваем сообщение
                await app.get_messages(post_link.split('/')[-2], int(post_link.split('/')[-1]))
        except Exception as e:
            print(f"[ViewService] Ошибка просмотра ({session_name}): {e}")

    async def add_views(self, post_link: str, max_sessions: int = 10):
        session_dirs = [f for f in os.listdir(self.sessions_path) if os.path.isdir(os.path.join(self.sessions_path, f))]
        random.shuffle(session_dirs)
        session_dirs = session_dirs[:max_sessions]

        tasks = []
        for session_name in session_dirs:
            tasks.append(self._send_view(session_name, post_link))

        delay = self.random_time_with_spread(self.action_time, self.random_percentage)
        print(f"Ждём {delay // 60} мин перед выполнением действия...")
        await asyncio.sleep(delay)


        action_duration = self.action_time * 60
        start_time = asyncio.get_event_loop().time()

        await asyncio.gather(*tasks, return_exceptions=True)

        elapsed_time = asyncio.get_event_loop().time() - start_time
        time_left = action_duration - elapsed_time
        if time_left > 0:
            print(f"Действие будет выполняться ещё {time_left // 60} мин...")
            await asyncio.sleep(time_left)
from pyrogram import Client
import asyncio
import os
import random


class ViewService:
    def __init__(self, sessions_path: str):
        self.sessions_path = sessions_path

    async def _send_view(self, session_name: str, post_link: str):
        try:
            async with Client(session_name, workdir=self.sessions_path) as app:
                await app.invoke_chat_action(chat_id=post_link.split('/')[-2], action="typing")
                await app.get_messages(post_link.split('/')[-2], int(post_link.split('/')[-1]))
        except Exception as e:
            print(f"[ViewService] Ошибка просмотра ({session_name}): {e}")

    async def add_views(self, post_link: str, max_sessions: int = 10):
        session_dirs = [f for f in os.listdir(self.sessions_path) if os.path.isdir(os.path.join(self.sessions_path, f))]
        random.shuffle(session_dirs)
        session_dirs = session_dirs[:max_sessions]

        tasks = [self._send_view(session_name, post_link) for session_name in session_dirs]
        await asyncio.gather(*tasks)

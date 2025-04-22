from pyrogram import Client
import asyncio
import os
import random


class ReactionService:
    def __init__(self, sessions_path: str):
        self.sessions_path = sessions_path

    async def _send_reaction(self, session_name: str, post_link: str, emoji: str):
        try:
            async with Client(session_name, workdir=self.sessions_path) as app:
                chat_id = post_link.split('/')[-2]
                message_id = int(post_link.split('/')[-1])
                await app.send_reaction(chat_id=chat_id, message_id=message_id, emoji=emoji)
        except Exception as e:
            print(f"[ReactionService] Ошибка реакции ({session_name}): {e}")

    async def react_to_post(self, post_link: str, emoji: str = "❤️", max_sessions: int = 10):
        session_dirs = [f for f in os.listdir(self.sessions_path) if os.path.isdir(os.path.join(self.sessions_path, f))]
        random.shuffle(session_dirs)
        session_dirs = session_dirs[:max_sessions]

        tasks = [self._send_reaction(session_name, post_link, emoji) for session_name in session_dirs]
        await asyncio.gather(*tasks)
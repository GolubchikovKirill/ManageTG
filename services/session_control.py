from pyrogram import Client
from pathlib import Path


class SessionManager:
    def __init__(self, session_folder: str = "sessions"):
        self.session_folder = Path(session_folder)
        self.session_folder.mkdir(parents=True, exist_ok=True)

    def get_session(self, phone_number: str, api_id: int, api_hash: str) -> Client:
        """
        Возвращает клиент сессии для указанного телефона.
        Если сессия не существует, создаёт новую сессию.
        """
        session_file = self.session_folder / f"{phone_number}.session"

        if session_file.exists():
            # Если сессия уже существует, возвращаем клиент с этой сессией
            return Client(str(session_file), api_id=api_id, api_hash=api_hash)
        else:
            # Если сессия не найдена, создаём новую сессию через авторизацию
            client = Client(
                f"{self.session_folder}/{phone_number}",
                api_id=api_id,
                api_hash=api_hash,
                phone_number=phone_number
            )
            return client
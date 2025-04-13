from pyrogram import Client, errors
from services.session_control import SessionManager

class TelegramAuth:
    def __init__(self, phone_number: str, api_id: int, api_hash: str, session_manager: SessionManager):
        self.phone_number = phone_number
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_manager = session_manager
        # Имя сессии теперь передается как часть имени файла
        self.client = Client(
            f"session_{phone_number}",  # Имя сессии - это просто имя файла
            api_id=self.api_id,
            api_hash=self.api_hash,
            phone_number=self.phone_number
        )

    async def send_code(self):
        try:
            # Запуск клиента и начало сессии
            await self.client.start()  # Это автоматически инициирует вход, если сессия еще не создана
            sent_code = await self.client.send_code(self.phone_number)
            return {"status": "ok", "phone_code_hash": sent_code.phone_code_hash}
        except errors.FloodWait as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def sign_in(self, code: str, phone_code_hash: str, password: str = None):
        try:
            # Проверка наличия пароля для двухфакторной аутентификации
            if password:
                # Передаем пароль, если он есть
                await self.client.sign_in(self.phone_number, code, phone_code_hash, password)
            else:
                # Если пароля нет, только код и хеш
                await self.client.sign_in(self.phone_number, code, phone_code_hash)
            return {"status": "ok"}
        except errors.PhoneCodeInvalid:
            return {"status": "error", "message": "Invalid code"}
        except errors.PhoneNumberFlood:
            return {"status": "error", "message": "Too many requests. Try again later."}
        except errors.PasswordHashInvalid:
            return {"status": "error", "message": "Invalid 2FA password"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
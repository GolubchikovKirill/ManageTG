import os
from pyrogram import Client, errors, types
from typing import Optional, Dict


class TelegramAuth:
    def __init__(
            self,
            phone_number: str,
            api_id: int,
            api_hash: str,
            proxy: Optional[Dict] = None,
            session_dir: str = "sessions"  # Добавлен параметр для пути сессий
    ):
        self.phone_number = phone_number
        self.api_id = api_id
        self.api_hash = api_hash
        self.proxy = proxy

        # Используем абсолютный путь для сессий
        self.session_path = os.path.abspath(session_dir)
        os.makedirs(self.session_path, exist_ok=True)

        self.client = Client(
            name=f"session_{phone_number}",
            workdir=self.session_path,
            api_id=api_id,
            api_hash=api_hash,
            phone_number=phone_number,
            proxy=proxy
        )

    async def send_code(self) -> Dict:
        """Отправляет код подтверждения на номер телефона."""
        try:
            await self.client.connect()
            sent_code = await self.client.send_code(self.phone_number)
            return {"status": "ok", "phone_code_hash": sent_code.phone_code_hash}
        except errors.FloodWait as e:
            return {"status": "error", "message": f"Flood wait: {e.value}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            await self.client.disconnect()  # Отключаемся после отправки кода

    async def sign_in(
            self,
            code: str,
            phone_code_hash: str,
            password: Optional[str] = None
    ) -> Dict:
        """Выполняет вход с кодом подтверждения и 2FA паролем при необходимости."""
        try:
            await self.client.connect()

            # Шаг 1: Попытка входа с кодом
            try:
                signed_in = await self.client.sign_in(
                    phone_number=self.phone_number,
                    phone_code_hash=phone_code_hash,
                    phone_code=code
                )
            except errors.SessionPasswordNeeded:
                # Требуется 2FA пароль
                if not password:
                    return {"status": "2fa_required", "message": "2FA password required"}

                # Шаг 2: Ввод 2FA пароля
                try:
                    await self.client.check_password(password=password)
                except errors.PasswordHashInvalid:
                    return {"status": "error", "message": "Invalid 2FA password"}
                signed_in = await self.client.get_me()

            # Проверка типа аккаунта
            if isinstance(signed_in, types.User) and signed_in.is_bot:
                return {"status": "error", "message": "Bot sessions not supported"}

            # Явно сохраняем сессию перед отключением
            await self.client.storage.save()
            return {"status": "ok"}

        except (errors.PhoneCodeInvalid, errors.PhoneCodeExpired):
            return {"status": "error", "message": "Invalid or expired code"}
        except errors.PhoneNumberFlood:
            return {"status": "error", "message": "Too many requests"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            if self.client.is_connected:
                await self.client.disconnect()

    async def get_session_path(self) -> str:
        """Возвращает путь к файлу сессии."""
        return self.client.storage.session_file
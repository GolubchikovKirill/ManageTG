import os
import re
from typing import Optional, Dict
from pyrogram import Client, errors, types


class TelegramAuth:
    def __init__(
        self,
        phone_number: str,
        api_id: int,
        api_hash: str,
        proxy: Optional[Dict] = None,
        session_dir: str = "sessions"
    ):
        self.phone_number = phone_number
        self.api_id = api_id
        self.api_hash = api_hash
        self.proxy = proxy
        self.phone_code_hash: Optional[str] = None

        # Безопасное имя для файла .session
        safe_name = re.sub(r"[^\w\d]", "_", phone_number)

        self.session_path = os.path.abspath(session_dir)
        os.makedirs(self.session_path, exist_ok=True)

        self.client = Client(
            name=f"session_{safe_name}",
            workdir=self.session_path,
            api_id=self.api_id,
            api_hash=self.api_hash,
            proxy=self.proxy
        )

        self._is_connected = False

    async def connect(self):
        if not self._is_connected:
            await self.client.connect()
            self._is_connected = True

    async def disconnect(self):
        if self._is_connected:
            await self.client.disconnect()
            self._is_connected = False

    async def send_code(self) -> Dict:
        try:
            await self.connect()
            sent_code = await self.client.send_code(self.phone_number)
            self.phone_code_hash = sent_code.phone_code_hash
            return {"status": "ok", "phone_code_hash": self.phone_code_hash}
        except errors.FloodWait as e:
            return {"status": "error", "message": f"Flood wait: {e.value} seconds"}
        except Exception as e:
            return {"status": "error", "message": f"Send code error: {str(e)}"}
        # УБИРАЕМ отключение — клиент должен остаться активным!
        # finally:
        #     await self.disconnect()

    async def sign_in(self, code: str, password: Optional[str] = None) -> Dict:
        try:
            await self.connect()

            if not self.phone_code_hash:
                return {"status": "error", "message": "No phone_code_hash. Send code first."}

            try:
                user = await self.client.sign_in(
                    phone_number=self.phone_number,
                    phone_code_hash=self.phone_code_hash,
                    phone_code=code
                )
            except errors.SessionPasswordNeeded:
                if not password:
                    return {"status": "2fa_required", "message": "2FA password required"}
                try:
                    await self.client.check_password(password)
                except errors.PasswordHashInvalid:
                    return {"status": "error", "message": "Invalid 2FA password"}
                user = await self.client.get_me()

            if isinstance(user, types.User) and user.is_bot:
                return {"status": "error", "message": "Bot sessions are not supported"}

            return {"status": "ok"}

        except errors.PhoneCodeInvalid:
            return {"status": "error", "message": "Invalid code"}
        except errors.PhoneCodeExpired:
            return {"status": "error", "message": "Code expired"}
        except errors.PhoneNumberFlood:
            return {"status": "error", "message": "Too many attempts. Try again later."}
        except Exception as e:
            return {"status": "error", "message": f"Sign in error: {str(e)}"}
        finally:
            await self.disconnect()

    def get_session_path(self) -> str:
        return self.client.storage.session_file
import os
from pyrogram import Client, errors


class TelegramAuth:
    def __init__(self, phone_number: str, api_id: int, api_hash: str):
        self.phone_number = phone_number
        self.api_id = api_id
        self.api_hash = api_hash

        session_path = os.path.join(os.getcwd(), "sessions")
        os.makedirs(session_path, exist_ok=True)

        session_name = f"{session_path}/session_{phone_number}"

        self.client = Client(
            session_name,
            api_id=self.api_id,
            api_hash=self.api_hash,
            phone_number=self.phone_number
        )

    async def send_code(self):
        try:
            await self.client.start()
            sent_code = await self.client.send_code(self.phone_number)
            return {"status": "ok", "phone_code_hash": sent_code.phone_code_hash}
        except errors.FloodWait as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def sign_in(self, code: str, phone_code_hash: str, password: str = None):
        try:
            if password:
                await self.client.sign_in(self.phone_number, code, phone_code_hash, password)
            else:
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

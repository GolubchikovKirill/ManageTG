import os
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded
from dotenv import load_dotenv
from database.models import Proxy

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")


def build_proxy_dict(proxy: Proxy) -> dict:
    """
    Преобразует объект Proxy из БД в формат, подходящий для pyrogram.
    """
    return {
        "hostname": proxy.ip_address,
        "port": proxy.port,
        "username": proxy.login,
        "password": proxy.password
    }


class TelegramAuth:
    def __init__(self, phone_number: str, proxy: dict = None):
        self.phone_number = phone_number
        self.client = Client(
            name=f"sessions/{self.phone_number}",
            api_id=API_ID,
            api_hash=API_HASH,
            in_memory=False,
            proxy=proxy
        )
        self.phone_code_hash = None

    async def send_code(self):
        await self.client.connect()
        sent_code = await self.client.send_code(self.phone_number)
        self.phone_code_hash = sent_code.phone_code_hash
        await self.client.disconnect()
        return {"status": "code_sent", "phone_code_hash": self.phone_code_hash}

    async def sign_in(self, code: str, phone_code_hash: str, password: str = None):
        await self.client.connect()

        try:
            await self.client.sign_in(
                phone_number=self.phone_number,
                phone_code_hash=phone_code_hash,
                phone_code=code
            )
        except SessionPasswordNeeded:
            if password is None:
                return {"status": "password_required"}
            await self.client.check_password(password)

        await self.client.disconnect()
        return {"status": "authorized"}
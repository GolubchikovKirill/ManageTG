from typing import Dict, Optional
from telegram_auth import TelegramAuth

auth_clients: Dict[str, TelegramAuth] = {}


async def get_auth(
        phone_number: str,
        api_id: int,
        api_hash: str,
        proxy: Optional[dict] = None
) -> TelegramAuth:
    if phone_number not in auth_clients:
        auth_clients[phone_number] = TelegramAuth(phone_number, api_id, api_hash, proxy)

    auth = auth_clients[phone_number]

    await auth.connect()
    return auth


async def clear_auth(phone_number: str):
    auth = auth_clients.pop(phone_number, None)
    if auth:
        try:
            await auth.disconnect()
        except Exception as e:
            print(f"[clear_auth] Error disconnecting {phone_number}: {e}")

import socket
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import Proxy
from app.schemas.proxy import AddProxyRequest


def is_proxy_available(ip: str, port: int, timeout: int = 3) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


async def add_or_update_proxy_repo(db: AsyncSession, data: AddProxyRequest) -> None:
    existing_proxy = await db.execute(select(Proxy).where(Proxy.port == data.port))
    existing_proxy = existing_proxy.scalars().first()

    if existing_proxy:
        existing_proxy.ip_address = data.ip_address
        existing_proxy.password = data.password
        existing_proxy.port = data.port
    else:
        new_proxy = Proxy(
            ip_address=data.ip_address,
            login=data.login,
            password=data.password,
            port=data.port
        )
        db.add(new_proxy)

    await db.commit()


async def delete_proxy_by_ip_repo(db: AsyncSession, ip_address: str) -> bool:
    result = await db.execute(select(Proxy).where(Proxy.ip_address == ip_address))
    proxy = result.scalar_one_or_none()
    if not proxy:
        return False

    await db.delete(proxy)
    await db.commit()
    return True


async def list_all_proxies_repo(db: AsyncSession) -> List[Proxy]:
    result = await db.execute(select(Proxy))
    return result.scalars().all()
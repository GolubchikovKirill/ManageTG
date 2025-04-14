import socket
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Proxy
from database.database import get_db

router = APIRouter(
    prefix="/proxy",
    tags=["Proxy"]
)


def is_proxy_available(ip: str, port: int, timeout: int = 3) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


@router.post("/add")
async def add_proxy(ip_address: str, port: int, login: str, password: str, db: AsyncSession = Depends(get_db)):
    if not is_proxy_available(ip_address, port):
        raise HTTPException(status_code=400, detail="Proxy is not available")

    result = await db.execute(select(Proxy).where(Proxy.ip_address == ip_address))
    existing_proxy = result.scalar_one_or_none()
    if existing_proxy:
        raise HTTPException(status_code=400, detail="Proxy with this IP already exists")

    proxy = Proxy(ip_address=ip_address, port=port, login=login, password=password)
    db.add(proxy)
    await db.commit()
    await db.refresh(proxy)
    return {"status": "success", "proxy_id": proxy.id}


@router.delete("/delete")
async def delete_proxy(ip_address: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Proxy).where(Proxy.ip_address == ip_address))
    proxy = result.scalar_one_or_none()
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy not found")

    await db.delete(proxy)
    await db.commit()
    return {"status": "deleted", "ip": ip_address}


@router.get("/list")
async def list_proxies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Proxy))
    proxies = result.scalars().all()
    return [
        {
            "id": proxy.id,
            "ip_address": proxy.ip_address,
            "port": proxy.port,
            "login": proxy.login,
            "password": proxy.password
        }
        for proxy in proxies
    ]
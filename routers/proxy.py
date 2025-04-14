import socket
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Proxy
from database.database import get_db

router = APIRouter(
    prefix="/proxy",
    tags=["Proxy"]
)


class AddProxyRequest(BaseModel):
    ip_address: str
    login: str
    password: str
    port: int


def is_proxy_available(ip: str, port: int, timeout: int = 3) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

@router.post("/add")
async def add_proxy(data: AddProxyRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Проверяем, существует ли уже прокси с таким логином
        existing_proxy = await db.execute(select(Proxy).where(Proxy.ip_address == data.ip_address))
        existing_proxy = existing_proxy.scalars().first()

        if existing_proxy:
            # Если прокси существует, обновляем его данные
            existing_proxy.ip_address = data.ip_address
            existing_proxy.password = data.password
            existing_proxy.port = data.port
        else:
            # Если прокси не существует, создаем новую запись
            new_proxy = Proxy(
                ip_address=data.ip_address,
                login=data.login,
                password=data.password,
                port=data.port
            )
            db.add(new_proxy)

        await db.commit()
        return {"message": "Proxy added or updated successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding proxy: {str(e)}")


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
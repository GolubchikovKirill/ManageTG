from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from schema_pydantic.schema_proxy import AddProxyRequest
from repositories.proxy_repo import (
    add_or_update_proxy_repo,
    delete_proxy_by_ip_repo,
    list_all_proxies_repo,
)

router = APIRouter(
    prefix="/proxy",
    tags=["Proxy"]
)


@router.post("/add")
async def add_proxy(data: AddProxyRequest, db: AsyncSession = Depends(get_db)):
    try:
        await add_or_update_proxy_repo(db, data)
        return {"message": "Proxy added or updated successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding proxy: {str(e)}")


@router.delete("/delete")
async def delete_proxy(ip_address: str, db: AsyncSession = Depends(get_db)):
    success = await delete_proxy_by_ip_repo(db, ip_address)
    if not success:
        raise HTTPException(status_code=404, detail="Proxy not found")
    return {"status": "deleted", "ip": ip_address}


@router.get("/list")
async def list_proxies(db: AsyncSession = Depends(get_db)):
    proxies = await list_all_proxies_repo(db)
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
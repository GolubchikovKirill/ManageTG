import socket
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.models import Proxy
from database.database import get_db

router = APIRouter(prefix="/proxy", tags=["Proxy"])


def is_proxy_available(ip: str, port: int, timeout: int = 3) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


@router.post("/add")
def add_proxy(ip_address: str, port: int, login: str, password: str, db: Session = Depends(get_db)):
    if not is_proxy_available(ip_address, port):
        raise HTTPException(status_code=400, detail="Proxy is not available")

    existing_proxy = db.query(Proxy).filter(Proxy.ip_address == ip_address).first()
    if existing_proxy:
        raise HTTPException(status_code=400, detail="Proxy with this IP already exists")

    proxy = Proxy(ip_address=ip_address, port=port, login=login, password=password)
    db.add(proxy)
    db.commit()
    db.refresh(proxy)
    return {"status": "success", "proxy_id": proxy.id}


@router.delete("/delete")
def delete_proxy(ip_address: str, db: Session = Depends(get_db)):
    proxy = db.query(Proxy).filter(Proxy.ip_address == ip_address).first()
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy not found")

    db.delete(proxy)
    db.commit()
    return {"status": "deleted", "ip": ip_address}


@router.get("/list")
def list_proxies(db: Session = Depends(get_db)):
    proxies = db.query(Proxy).all()
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
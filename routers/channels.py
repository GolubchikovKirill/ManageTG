from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.models import Channels
from database.database import async_session
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
from typing import Optional

# Схема для добавления канала
class ChannelCreate(BaseModel):
    name: str
    comment: str
    status: Optional[str] = "open"  # Канал может быть "open" или "private"

# Схема для представления канала
class ChannelResponse(BaseModel):
    id: int
    name: str
    comment: str
    status: str
    request_count: int
    accepted_request_count: int

    class Config:
        from_attributes = True


router = APIRouter()


# Зависимость для получения сессии базы данных
def get_db():
    db = async_session()
    try:
        yield db
    finally:
        db.close()


# Роут для добавления нового канала
@router.post("/channels/", response_model=ChannelResponse)
def create_channel(channel: ChannelCreate, db: Session = Depends(get_db)):
    try:
        db_channel = Channels(
            name=channel.name,
            comment=channel.comment,
            status=channel.status
        )
        db.add(db_channel)
        db.commit()
        db.refresh(db_channel)
        return db_channel
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))


# Роут для получения списка всех каналов
@router.get("/channels/", response_model=List[ChannelResponse])
def get_channels(db: Session = Depends(get_db)):
    try:
        channels = db.query(Channels).all()
        return channels
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))


# Роут для удаления канала по ID
@router.delete("/channels/{channel_id}", response_model=ChannelResponse)
def delete_channel(channel_id: int, db: Session = Depends(get_db)):
    try:
        db_channel = db.query(Channels).filter(Channels.id == channel_id).first()
        if db_channel is None:
            raise HTTPException(status_code=404, detail="Channel not found")

        db.delete(db_channel)
        db.commit()
        return db_channel
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
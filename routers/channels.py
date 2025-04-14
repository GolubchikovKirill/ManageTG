from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import pytz

from database.models import Channels
from database.database import get_db

router = APIRouter(
    prefix="/channels",
    tags=["channels"],
)

# Схема для добавления канала
class ChannelCreate(BaseModel):
    name: str
    comment: str
    status: Optional[str] = "open"  # Канал может быть "open" или "private"

# Схема для ответа
class ChannelResponse(BaseModel):
    id: int
    name: str
    comment: str
    status: str
    request_count: int
    accepted_request_count: int

    class Config:
        from_attributes = True


# Роут для добавления нового канала
@router.post("/channels/", response_model=ChannelResponse)
async def create_channel(channel: ChannelCreate, db: AsyncSession = Depends(get_db)):
    try:
        created_at = datetime.now(pytz.utc).replace(tzinfo=None)
        updated_at = datetime.now(pytz.utc).replace(tzinfo=None)

        new_channel = Channels(
            name=channel.name,
            comment=channel.comment,
            status=channel.status,
            created_at=created_at,
            updated_at=updated_at
        )
        db.add(new_channel)
        await db.commit()
        await db.refresh(new_channel)
        return new_channel
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# Роут для получения списка всех каналов
@router.get("/channels/", response_model=List[ChannelResponse])
async def get_channels(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Channels))
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# Роут для удаления канала по ID
@router.delete("/channels/{channel_id}", response_model=ChannelResponse)
async def delete_channel(channel_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Channels).where(Channels.id == channel_id))
        channel = result.scalar_one_or_none()

        if channel is None:
            raise HTTPException(status_code=404, detail="Channel not found")

        await db.delete(channel)
        await db.commit()
        return channel
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

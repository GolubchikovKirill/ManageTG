from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import List

from app.core.db import get_db
from app.schemas.channels import ChannelCreate, ChannelResponse
from app.repositories.channels import (
    create_channel_repo,
    get_all_channels_repo,
    delete_channel_repo
)

router = APIRouter(
    prefix="/channels",
    tags=["channels"],
)


@router.post("/create", response_model=ChannelResponse)
async def create_channel(channel: ChannelCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await create_channel_repo(db, channel)
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/get", response_model=List[ChannelResponse])
async def get_channels(db: AsyncSession = Depends(get_db)):
    try:
        return await get_all_channels_repo(db)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.delete("/delete/{channel_id}", response_model=ChannelResponse)
async def delete_channel(channel_id: int, db: AsyncSession = Depends(get_db)):
    try:
        channel = await delete_channel_repo(db, channel_id)
        if channel is None:
            raise HTTPException(status_code=404, detail="Channel not found")
        return channel
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

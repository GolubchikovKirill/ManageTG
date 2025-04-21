from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
import pytz

from database.models import Channels
from schema_pydantic.schema_channels import ChannelCreate

async def create_channel_repo(db: AsyncSession, channel_data: ChannelCreate) -> Channels:
    created_at = datetime.now(pytz.utc).replace(tzinfo=None)
    updated_at = datetime.now(pytz.utc).replace(tzinfo=None)

    new_channel = Channels(
        name=channel_data.name,
        comment=channel_data.comment,
        status=channel_data.status,
        created_at=created_at,
        updated_at=updated_at
    )
    db.add(new_channel)
    await db.commit()
    await db.refresh(new_channel)
    return new_channel


async def get_all_channels_repo(db: AsyncSession) -> List[Channels]:
    result = await db.execute(select(Channels))
    return result.scalars().all()


async def delete_channel_repo(db: AsyncSession, channel_id: int) -> Optional[Channels]:
    result = await db.execute(select(Channels).where(Channels.id == channel_id))
    channel = result.scalar_one_or_none()

    if channel:
        await db.delete(channel)
        await db.commit()
    return channel
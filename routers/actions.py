from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.database import get_db
from database.models import Actions

router = APIRouter(
    prefix="/actions",
    tags=["Actions"]
)

class ActionCreate(BaseModel):
    channel_id: int
    action_type: str
    count: int
    action_time: int
    random_percentage: int

class ActionResponse(BaseModel):
    id: int
    channel_id: int
    action_type: str
    count: int
    action_time: int
    random_percentage: int

    class Config:
        from_attributes = True


@router.post("/", response_model=ActionResponse)
async def create_action(action: ActionCreate, db: AsyncSession = Depends(get_db)):
    try:
        new_action = Actions(
            channel_id=action.channel_id,
            action_type=action.action_type,
            count=action.count,
            action_time=action.action_time,
            random_percentage=action.random_percentage
        )
        db.add(new_action)
        await db.commit()
        await db.refresh(new_action)
        return new_action
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating action: {str(e)}")


@router.get("/", response_model=list[ActionResponse])
async def get_actions(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Actions))
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting actions: {str(e)}")


@router.delete("/{action_id}", response_model=ActionResponse)
async def delete_action(action_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Actions).where(Actions.id == action_id))
        action = result.scalar_one_or_none()

        if action is None:
            raise HTTPException(status_code=404, detail="Action not found")

        await db.delete(action)
        await db.commit()
        return action
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting action: {str(e)}")


@router.put("/{action_id}", response_model=ActionResponse)
async def update_action(action_id: int, action: ActionCreate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Actions).where(Actions.id == action_id))
        existing_action = result.scalar_one_or_none()

        if existing_action is None:
            raise HTTPException(status_code=404, detail="Action not found")

        existing_action.channel_id = action.channel_id
        existing_action.action_type = action.action_type
        existing_action.count = action.count
        existing_action.action_time = action.action_time
        existing_action.random_percentage = action.random_percentage

        await db.commit()
        await db.refresh(existing_action)
        return existing_action
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating action: {str(e)}")
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from schema_pydantic.schema_actions import ActionCreate, ActionResponse
from repositories.actions_repo import (
    create_action,
    get_all_actions,
    get_action_by_id,
    delete_action as delete_action_db,
    update_action as update_action_db,
)

router = APIRouter(
    prefix="/actions",
    tags=["Actions"]
)


@router.post("/", response_model=ActionResponse)
async def create_action_route(action: ActionCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await create_action(db, action)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating action: {str(e)}")


@router.get("/", response_model=list[ActionResponse])
async def get_actions_route(db: AsyncSession = Depends(get_db)):
    try:
        return await get_all_actions(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting actions: {str(e)}")


@router.delete("/{action_id}", response_model=ActionResponse)
async def delete_action_route(action_id: int, db: AsyncSession = Depends(get_db)):
    try:
        action = await get_action_by_id(db, action_id)
        if not action:
            raise HTTPException(status_code=404, detail="Action not found")

        await delete_action_db(db, action)
        return action
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting action: {str(e)}")


@router.put("/{action_id}", response_model=ActionResponse)
async def update_action_route(action_id: int, action: ActionCreate, db: AsyncSession = Depends(get_db)):
    try:
        existing_action = await get_action_by_id(db, action_id)
        if not existing_action:
            raise HTTPException(status_code=404, detail="Action not found")

        return await update_action_db(db, existing_action, action)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating action: {str(e)}")
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from database.enum_db import ActionType
from database.database import get_db
from schema_pydantic.schema_comment import ActionCreate, ActionResponse
from repositories.comments_repo import (
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


@router.post("/{action_type}", response_model=ActionResponse)
async def create_action_route(
        action_type: ActionType = Path(...),
        action: ActionCreate = Depends(),
        db: AsyncSession = Depends(get_db)
):
    try:
        return await create_action(db, action, action_type.value)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating action: {str(e)}")


@router.get("/{action_type}", response_model=list[ActionResponse])
async def get_actions_route(
        action_type: ActionType = Path(...),
        db: AsyncSession = Depends(get_db)
):
    try:
        return await get_all_actions(db, action_type.value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting actions: {str(e)}")


@router.get("/{action_type}/{action_id}", response_model=ActionResponse)
async def get_action_route(
        action_type: ActionType = Path(...),
        action_id: int = Path(...),
        db: AsyncSession = Depends(get_db)
):
    try:
        action = await get_action_by_id(db, action_id, action_type.value)
        if not action:
            raise HTTPException(status_code=404, detail="Action not found")
        return action
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting action: {str(e)}")


@router.delete("/{action_type}/{action_id}", response_model=ActionResponse)
async def delete_action_route(
        action_type: ActionType = Path(...),
        action_id: int = Path(...),
        db: AsyncSession = Depends(get_db)
):
    try:
        action = await get_action_by_id(db, action_id, action_type.value)
        if not action:
            raise HTTPException(status_code=404, detail="Action not found")

        await delete_action_db(db, action_type.value, action_id)
        return action
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting action: {str(e)}")


@router.put("/{action_type}/{action_id}", response_model=ActionResponse)
async def update_action_route(
        action_type: ActionType = Path(...),
        action_id: int = Path(...),
        action: ActionCreate = Depends(),
        db: AsyncSession = Depends(get_db)
):
    try:
        updated = await update_action_db(db, action_id, action, action_type.value)
        if not updated:
            raise HTTPException(status_code=404, detail="Action not found")
        return updated
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating action: {str(e)}")

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from services.openai_service import OpenAIService
from services.commenting_logic import BotActionExecutor
from repositories.launching_repo import get_action_by_id

router = APIRouter(
    prefix="/launching_actions",
    tags=["launching_actions"],
)

@router.post("/execute-action")
async def execute_bot_action(
        action_id: int,
        api_id: str,
        api_hash: str,
        db: AsyncSession = Depends(get_db)
):
    """
    Запуск действия для всех сессий (комментарий, реакция, просмотр).
    """
    action = await get_action_by_id(db, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    openai_service = OpenAIService()
    bot_executor = BotActionExecutor(session=db, openai_service=openai_service)
    await bot_executor.run(action=action, api_id=api_id, api_hash=api_hash)

    return {"message": "Action executed successfully"}
from pydantic import BaseModel, Field
from database.models import ActionType

class ActionCreate(BaseModel):
    channel_id: int  # ID канала, для которого выполняется действие
    action_type: ActionType  # Тип действия (например, комментирование, реакция и т. д.)
    positive_count: int = Field(ge=0)  # Количество положительных комментариев
    negative_count: int = Field(ge=0)  # Количество негативных комментариев
    critical_count: int = Field(ge=0)  # Количество критических комментариев
    question_count: int = Field(ge=0)  # Количество вопросительных комментариев
    custom_prompt: str | None = None  # Пользовательский промпт для действия
    action_time: int = Field(gt=0, le=3600)  # Время действия в секундах (от 1 до 3600)
    random_percentage: int = Field(ge=0, le=100)  # Процент случайной вариации времени действия


class ActionResponse(ActionCreate):
    id: int

    class Config:
        from_attributes = True
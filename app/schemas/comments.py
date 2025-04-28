from pydantic import BaseModel, Field
from typing import Optional


# Базовая модель для всех комментариев
class CommentActionBase(BaseModel):
    channel_id: int
    action_time: int = Field(gt=0, le=3600)  # Время действия в секундах (до 1 часа)
    random_percentage: int = Field(ge=0, le=100)  # Процент разброса времени (0-100)
    custom_prompt: Optional[str] = None  # Кастомный промпт (если требуется)


# Модель для создания нового задания на комментирование
class CommentActionCreate(CommentActionBase):
    positive_count: Optional[int] = Field(0, ge=0)
    neutral_count: Optional[int] = Field(0, ge=0)
    critical_count: Optional[int] = Field(0, ge=0)
    question_count: Optional[int] = Field(0, ge=0)
    custom_count: Optional[int] = Field(0, ge=0)
    custom_prompt: Optional[str] = None


# Модель для ответа при получении задания
class CommentActionResponse(CommentActionBase):
    id: int
    positive_count: int
    neutral_count: int
    critical_count: int
    question_count: int
    custom_count: int

    class Config:
        from_attributes = True
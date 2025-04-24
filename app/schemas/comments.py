from pydantic import BaseModel, Field

class CommentActionCreate(BaseModel):
    channel_id: int
    positive_count: int = Field(ge=0)
    neutral_count: int = Field(ge=0)
    critical_count: int = Field(ge=0)
    question_count: int = Field(ge=0)
    custom_prompt: str | None = None
    action_time: int = Field(gt=0, le=3600)
    random_percentage: int = Field(ge=0, le=100)

class CommentActionResponse(CommentActionCreate):
    id: int

    class Config:
        from_attributes = True
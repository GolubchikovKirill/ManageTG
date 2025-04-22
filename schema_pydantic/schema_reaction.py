from pydantic import BaseModel, Field

class ReactionActionCreate(BaseModel):
    channel_id: int
    reaction_type: str
    count: int = Field(gt=0)
    action_time: int = Field(gt=0, le=3600)
    random_percentage: int = Field(ge=0, le=100)

class ReactionActionResponse(ReactionActionCreate):
    id: int

    class Config:
        from_attributes = True
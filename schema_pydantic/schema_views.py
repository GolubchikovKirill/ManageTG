from pydantic import BaseModel, Field

class ViewActionCreate(BaseModel):
    channel_id: int
    count: int = Field(gt=0)
    action_time: int = Field(gt=0, le=3600)
    random_percentage: int = Field(ge=0, le=100)

class ViewActionResponse(ViewActionCreate):
    id: int

    class Config:
        from_attributes = True
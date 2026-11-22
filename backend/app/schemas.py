from pydantic import BaseModel, Field


class MissionCreate(BaseModel):
    objective: str = Field(min_length=3, max_length=4000)
    source: str = "web"


class MissionCreated(BaseModel):
    id: str
    status: str

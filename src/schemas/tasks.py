from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class STaskAdd(BaseModel):
    title: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=200)


class STask(STaskAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class STaskId(BaseModel):
    task_id: int


class STaskDelete(BaseModel):
    ok: bool = True
    message: str

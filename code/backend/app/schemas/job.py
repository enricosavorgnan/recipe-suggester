from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    running = "running"
    completed = "completed"
    failed = "failed"


class IngredientsJobResponse(BaseModel):
    id: int
    recipe_id: int
    status: JobStatus
    ingredients_json: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]

    class Config:
        from_attributes = True


class RecipeJobResponse(BaseModel):
    id: int
    recipe_id: int
    status: JobStatus
    recipe_json: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]

    class Config:
        from_attributes = True


class UpdateIngredientsRequest(BaseModel):
    ingredients_json: str

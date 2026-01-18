from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.category import CategoryResponse


class RecipeCreate(BaseModel):
    pass


class RecipeUpdate(BaseModel):
    title: str


class RecipeResponse(BaseModel):
    id: int
    user_id: int
    category_id: Optional[int]
    title: str
    image: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class RecipeWithCategory(RecipeResponse):
    category: Optional[CategoryResponse]

    class Config:
        from_attributes = True

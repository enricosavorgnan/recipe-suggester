from pydantic import BaseModel
from datetime import datetime


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AssignCategoryRequest(BaseModel):
    recipe_ids: list[int]
    category_id: int | None = None

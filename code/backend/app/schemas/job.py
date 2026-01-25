from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    running = "running"
    completed = "completed"
    failed = "failed"


class Ingredient(BaseModel):
    """Single ingredient with optional confidence score from ML detection"""
    name: str = Field(..., min_length=1, description="Ingredient name")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="ML confidence score (0-1), null for user-added ingredients")


class IngredientsData(BaseModel):
    """Complete ingredients detection result"""
    ingredients: List[Ingredient] = Field(..., min_items=1, description="List of detected/added ingredients")
    success: bool = Field(True, description="Whether detection was successful")

    @field_validator('ingredients')
    @classmethod
    def validate_ingredients_not_empty(cls, v):
        if not v:
            raise ValueError('At least one ingredient is required')
        return v


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
    """Request to update ingredients data"""
    ingredients_data: IngredientsData

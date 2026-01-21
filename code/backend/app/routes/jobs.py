from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.job import IngredientsJobResponse, RecipeJobResponse
from app.services import job_service


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/ingredients/{recipe_id}", response_model=IngredientsJobResponse, status_code=status.HTTP_201_CREATED)
def create_ingredients_job(
    recipe_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates an ingredients detection job for a recipe.
    Returns immediately while ML processing runs in background.
    """
    return job_service.create_ingredients_job(db, recipe_id, current_user.id, background_tasks)


@router.get("/ingredients/{job_id}", response_model=IngredientsJobResponse)
def get_ingredients_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Gets status of ingredients detection job.
    Poll this endpoint to check when processing is complete.
    """
    return job_service.get_ingredients_job(db, job_id, current_user.id)


@router.get("/recipe/{job_id}", response_model=RecipeJobResponse)
def get_recipe_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Gets status of recipe generation job.
    Poll this endpoint to check when processing is complete.
    """
    return job_service.get_recipe_job(db, job_id, current_user.id)

from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.job import IngredientsJobResponse, RecipeJobResponse, UpdateIngredientsRequest
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


@router.put("/ingredients/{recipe_id}", response_model=IngredientsJobResponse)
def update_ingredients_json(
    recipe_id: int,
    request: UpdateIngredientsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates the ingredients JSON for a recipe after user edits.
    Can only update completed ingredients jobs.
    Validates ingredient structure with confidence scores.
    """
    return job_service.update_ingredients_json(
        db,
        recipe_id,
        current_user.id,
        request.ingredients_data.model_dump()
    )


@router.post("/recipe/{recipe_id}", response_model=RecipeJobResponse, status_code=status.HTTP_201_CREATED)
def create_recipe_job(
    recipe_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually triggers recipe generation job after user edits ingredients.
    Requires ingredients detection to be completed first.
    """
    return job_service.create_recipe_job(db, recipe_id, current_user.id, background_tasks)


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


@router.get("/by-recipe/{recipe_id}")
def get_jobs_by_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Gets both ingredients and recipe jobs for a specific recipe.
    """
    return job_service.get_jobs_by_recipe(db, recipe_id, current_user.id)

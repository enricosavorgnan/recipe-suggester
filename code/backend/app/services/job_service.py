from sqlalchemy.orm import Session
from fastapi import HTTPException, status, BackgroundTasks
from datetime import datetime
import asyncio
import json
from app.models.job import IngredientsJob, RecipeJob, JobStatus
from app.models.recipe import Recipe
from app.services.llm_service import generate_recipe_from_ingredients


def create_ingredients_job(db: Session, recipe_id: int, user_id: int, background_tasks: BackgroundTasks = None) -> IngredientsJob:
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id, Recipe.user_id == user_id).first()
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    # Check if job already exists
    existing_job = db.query(IngredientsJob).filter(IngredientsJob.recipe_id == recipe_id).first()
    if existing_job:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ingredients job already exists for this recipe")

    job = IngredientsJob(recipe_id=recipe_id, status=JobStatus.running)
    db.add(job)
    db.commit()
    db.refresh(job)

    # Launch async task to process ingredients (if background_tasks provided)
    if background_tasks:
        background_tasks.add_task(process_ingredients_async, job.id)

    return job


def get_ingredients_job(db: Session, job_id: int, user_id: int) -> IngredientsJob:
    job = db.query(IngredientsJob).join(Recipe).filter(
        IngredientsJob.id == job_id,
        Recipe.user_id == user_id
    ).first()

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredients job not found")

    return job


async def process_ingredients_async(job_id: int):
    """
    Async task that simulates ML model processing for ingredient detection.
    Updates job status and launches recipe generation when done.
    """
    from app.db.database import SessionLocal

    db = SessionLocal()
    try:
        # Simulate ML processing time
        await asyncio.sleep(5)

        # Mock ingredients detection result
        mock_ingredients = {
            "ingredients": [
                {"name": "Tomato", "confidence": 0.95},
                {"name": "Onion", "confidence": 0.88},
                {"name": "Garlic", "confidence": 0.72},
                {"name": "Olive Oil", "confidence": 0.65}
            ]
        }

        job = db.query(IngredientsJob).filter(IngredientsJob.id == job_id).first()
        if job:
            job.status = JobStatus.completed
            job.ingredients_json = json.dumps(mock_ingredients)
            job.end_time = datetime.utcnow()
            db.commit()

    except Exception as e:
        job = db.query(IngredientsJob).filter(IngredientsJob.id == job_id).first()
        if job:
            job.status = JobStatus.failed
            job.end_time = datetime.utcnow()
            db.commit()
    finally:
        db.close()


def create_recipe_job(db: Session, recipe_id: int, user_id: int, ingredients: list[dict], background_tasks: BackgroundTasks = None) -> RecipeJob:
    """
    Creates a recipe generation job with the provided ingredients.
    """
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id, Recipe.user_id == user_id).first()
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    # Check if ingredients job is completed
    ingredients_job = db.query(IngredientsJob).filter(IngredientsJob.recipe_id == recipe_id).first()
    if not ingredients_job or ingredients_job.status != JobStatus.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ingredients detection must be completed first"
        )

    # Check if recipe job already exists
    existing_job = db.query(RecipeJob).filter(RecipeJob.recipe_id == recipe_id).first()
    if existing_job:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Recipe job already exists for this recipe")

    job = RecipeJob(recipe_id=recipe_id, status=JobStatus.running)
    db.add(job)
    db.commit()
    db.refresh(job)

    # Launch async task to process recipe (if background_tasks provided)
    if background_tasks:
        background_tasks.add_task(process_recipe_async, job.id, ingredients)

    return job


def get_recipe_job(db: Session, job_id: int, user_id: int) -> RecipeJob:
    job = db.query(RecipeJob).join(Recipe).filter(
        RecipeJob.id == job_id,
        Recipe.user_id == user_id
    ).first()

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe job not found")

    return job


async def process_recipe_async(job_id: int, ingredients: list[dict]):
    """
    Async task that uses LLM for recipe generation.
    Updates job status when done.
    """
    from app.db.database import SessionLocal

    db = SessionLocal()
    try:
        # Extract ingredient names from the list (ignore confidence)
        ingredient_names = [ing.get("name", "") for ing in ingredients if ing.get("name")]

        # Generate recipe using LLM
        recipe_dict = generate_recipe_from_ingredients(ingredient_names)

        job = db.query(RecipeJob).filter(RecipeJob.id == job_id).first()
        if job:
            job.status = JobStatus.completed
            job.recipe_json = json.dumps(recipe_dict)
            job.end_time = datetime.utcnow()
            db.commit()

    except Exception as e:
        print(f"Error in process_recipe_async: {e}")
        job = db.query(RecipeJob).filter(RecipeJob.id == job_id).first()
        if job:
            job.status = JobStatus.failed
            job.end_time = datetime.utcnow()
            db.commit()
    finally:
        db.close()


def get_jobs_by_recipe(db: Session, recipe_id: int, user_id: int):
    """
    Gets both ingredients and recipe jobs for a specific recipe.
    """
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id, Recipe.user_id == user_id).first()
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    ingredients_job = db.query(IngredientsJob).filter(IngredientsJob.recipe_id == recipe_id).first()
    recipe_job = db.query(RecipeJob).filter(RecipeJob.recipe_id == recipe_id).first()

    return {
        "ingredients_job": ingredients_job,
        "recipe_job": recipe_job
    }

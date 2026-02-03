from sqlalchemy.orm import Session
from fastapi import HTTPException, status, BackgroundTasks
from datetime import datetime
import asyncio
import json
from app.models.job import IngredientsJob, RecipeJob, JobStatus
from app.models.recipe import Recipe


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


def update_ingredients_json(db: Session, recipe_id: int, user_id: int, ingredients_data: dict) -> IngredientsJob:
    """
    Updates the ingredients JSON for a completed ingredients job.
    Allows users to edit detected ingredients before generating recipe.
    The ingredients_data is already validated by Pydantic schema.
    """
    # Get recipe and verify ownership
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id, Recipe.user_id == user_id).first()
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    # Get ingredients job
    job = db.query(IngredientsJob).filter(IngredientsJob.recipe_id == recipe_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredients job not found")

    # Only allow updates if job is completed
    if job.status != JobStatus.completed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot update ingredients while job is still running")

    # Convert validated data to JSON string for storage
    job.ingredients_json = json.dumps(ingredients_data)
    db.commit()
    db.refresh(job)

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

        # Mock ingredients detection result with confidence scores
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


def create_recipe_job(db: Session, recipe_id: int, user_id: int, background_tasks: BackgroundTasks = None) -> RecipeJob:
    """
    Manually creates a recipe generation job for a recipe.
    Requires that ingredients job is completed first.
    """
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id, Recipe.user_id == user_id).first()
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    # Check that ingredients job exists and is completed
    ingredients_job = db.query(IngredientsJob).filter(IngredientsJob.recipe_id == recipe_id).first()
    if not ingredients_job:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ingredients job not found. Run ingredient detection first.")

    if ingredients_job.status != JobStatus.completed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ingredients job must be completed before generating recipe")

    # Check if recipe job already exists
    existing_job = db.query(RecipeJob).filter(RecipeJob.recipe_id == recipe_id).first()
    if existing_job:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Recipe job already exists for this recipe")

    job = RecipeJob(recipe_id=recipe_id, status=JobStatus.running)
    db.add(job)
    db.commit()
    db.refresh(job)

    # Launch async task to generate recipe (if background_tasks provided)
    if background_tasks:
        background_tasks.add_task(process_recipe_async, job.id)

    return job


def get_recipe_job(db: Session, job_id: int, user_id: int) -> RecipeJob:
    job = db.query(RecipeJob).join(Recipe).filter(
        RecipeJob.id == job_id,
        Recipe.user_id == user_id
    ).first()

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe job not found")

    return job


async def process_recipe_async(job_id: int):
    """
    Async task that simulates LLM processing for recipe generation.
    Updates job status when done.
    """
    from app.db.database import SessionLocal

    db = SessionLocal()
    try:
        # Simulate LLM processing time
        await asyncio.sleep(8)

        # Mock recipe generation result
        mock_recipe = {
            "title": "Tomato and Garlic Pasta",
            "instructions": [
                "Chop the onions and garlic",
                "Dice the tomatoes",
                "Sauté onions and garlic in olive oil",
                "Add tomatoes and simmer for 20 minutes",
                "Serve over pasta"
            ],
            "cooking_time": "30 minutes",
            "servings": 4
        }

        job = db.query(RecipeJob).filter(RecipeJob.id == job_id).first()
        if job:
            job.status = JobStatus.completed
            job.recipe_json = json.dumps(mock_recipe)
            job.end_time = datetime.utcnow()
            db.commit()

    except Exception as e:
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

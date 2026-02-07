import os
from pathlib import Path
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
    Async task that calls the models service for ingredient detection from image.
    Updates job status when done.
    """
    import httpx
    from app.db.database import SessionLocal
    from app.config.settings import settings

    db = SessionLocal()
    try:
        # Get the job and recipe
        job = db.query(IngredientsJob).filter(IngredientsJob.id == job_id).first()
        if not job:
            return

        recipe = db.query(Recipe).filter(Recipe.id == job.recipe_id).first()
        if not recipe or not recipe.image:
            raise ValueError("Recipe or image not found")

        # images are stored in uploads/recipes/
        # Use absolute path so models service can find it when running locally
        from app.services.recipe_service import UPLOAD_DIR
        image_path = str((UPLOAD_DIR / recipe.image).resolve())

        # Call models service via HTTP
        models_service_url = f"{settings.MODELS_SERVICE_URL}/predict"
        print(f"[Models Service] Calling {models_service_url} for image: {image_path}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                models_service_url,
                json={"image_path": image_path}
            )
            response.raise_for_status()
            result = response.json()

        # Extract ingredients from response
        ingredients_data = result.get("ingredients", [])
        print(f"[Models Service] Detected {len(ingredients_data)} ingredients")

        ingredients_json_str = json.dumps(ingredients_data)

        # Update job with results
        job.status = JobStatus.completed
        job.ingredients_json = ingredients_json_str
        job.end_time = datetime.utcnow()
        db.commit()
        print(f"[DEBUG] Job {job.id} completed successfully")

    # set the job as failed in the db of something goes wrong
    except httpx.HTTPStatusError as e:
        print(f"[Models Service] HTTP error: {e.response.status_code} - {e.response.text}")
        job = db.query(IngredientsJob).filter(IngredientsJob.id == job_id).first()
        if job:
            job.status = JobStatus.failed
            job.end_time = datetime.utcnow()
            db.commit()
    except httpx.RequestError as e:
        print(f"[Models Service] Request error: {e}")
        job = db.query(IngredientsJob).filter(IngredientsJob.id == job_id).first()
        if job:
            job.status = JobStatus.failed
            job.end_time = datetime.utcnow()
            db.commit()
    except Exception as e:
        print(f"Error in process_ingredients_async: {e}")
        job = db.query(IngredientsJob).filter(IngredientsJob.id == job_id).first()
        if job:
            job.status = JobStatus.failed
            job.end_time = datetime.utcnow()
            db.commit()
    finally:
        db.close()


def create_recipe_job(db: Session, recipe_id: int, user_id: int, ingredients: list[dict], background_tasks: BackgroundTasks = None) -> RecipeJob:
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

        if not ingredient_names:
            raise ValueError("No ingredients provided")

        # Generate recipe using LLM
        recipe_dict = generate_recipe_from_ingredients(ingredient_names)

        job = db.query(RecipeJob).filter(RecipeJob.id == job_id).first()
        if job:
            # Update the Recipe table with the generated title
            recipe = db.query(Recipe).filter(Recipe.id == job.recipe_id).first()
            if recipe and "title" in recipe_dict:
                old_title = recipe.title
                recipe.title = recipe_dict["title"]
                print(f"[Recipe Title Update] Recipe ID {recipe.id}: '{old_title}' -> '{recipe.title}'")
            else:
                print(f"[Recipe Title Update] SKIPPED - recipe: {recipe}, has title: {'title' in recipe_dict}")

            # Update the job with recipe JSON
            job.status = JobStatus.completed
            job.recipe_json = json.dumps(recipe_dict)
            job.end_time = datetime.utcnow()
            db.commit()

    except Exception as e:
        error_msg = str(e)
        print(f"Error in process_recipe_async: {error_msg}")

        # Check for specific OpenAI errors
        if "rate_limit" in error_msg.lower() or "quota" in error_msg.lower():
            print("OpenAI API rate limit or quota exceeded")
        elif "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            print("OpenAI API authentication error - check API key")

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

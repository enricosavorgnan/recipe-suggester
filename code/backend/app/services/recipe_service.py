from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from datetime import datetime
from pathlib import Path
import secrets
import shutil
from app.models.recipe import Recipe


UPLOAD_DIR = Path("uploads/recipes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def create_recipe(db: Session, user_id: int) -> Recipe:
    now = datetime.utcnow()
    title = now.strftime("Recipe of %d/%m/%y %H:%M")

    recipe = Recipe(user_id=user_id, title=title)
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


def get_user_recipes(db: Session, user_id: int, category_id: int | None = None) -> list[Recipe]:
    query = db.query(Recipe).filter(Recipe.user_id == user_id)

    if category_id is not None:
        query = query.filter(Recipe.category_id == category_id)

    return query.order_by(Recipe.created_at.desc()).all()


def get_recipe(db: Session, recipe_id: int, user_id: int) -> Recipe:
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id, Recipe.user_id == user_id).first()
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return recipe


def update_recipe_title(db: Session, recipe_id: int, user_id: int, new_title: str) -> Recipe:
    recipe = get_recipe(db, recipe_id, user_id)
    recipe.title = new_title
    db.commit()
    db.refresh(recipe)
    return recipe


def delete_recipe(db: Session, recipe_id: int, user_id: int) -> None:
    recipe = get_recipe(db, recipe_id, user_id)

    if recipe.image:
        image_path = UPLOAD_DIR / recipe.image
        if image_path.exists():
            image_path.unlink()

    db.delete(recipe)
    db.commit()


def upload_recipe_image(db: Session, recipe_id: int, user_id: int, file: UploadFile) -> Recipe:
    recipe = get_recipe(db, recipe_id, user_id)

    if recipe.image:
        old_image_path = UPLOAD_DIR / recipe.image
        if old_image_path.exists():
            old_image_path.unlink()

    file_extension = Path(file.filename).suffix if file.filename else ".jpg"
    random_name = f"{secrets.token_hex(16)}{file_extension}"
    file_path = UPLOAD_DIR / random_name

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    recipe.image = random_name
    db.commit()
    db.refresh(recipe)
    return recipe

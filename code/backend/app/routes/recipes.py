from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.recipe import RecipeResponse, RecipeWithCategory, RecipeUpdate
from app.services import recipe_service


router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.post("", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def create_recipe(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return recipe_service.create_recipe(db, current_user.id)


@router.get("", response_model=list[RecipeWithCategory])
def get_recipes(
    category_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return recipe_service.get_user_recipes(db, current_user.id, category_id)


@router.get("/{recipe_id}", response_model=RecipeWithCategory)
def get_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return recipe_service.get_recipe(db, recipe_id, current_user.id)


@router.patch("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: int,
    data: RecipeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return recipe_service.update_recipe_title(db, recipe_id, current_user.id, data.title)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recipe_service.delete_recipe(db, recipe_id, current_user.id)


@router.post("/{recipe_id}/upload", response_model=RecipeResponse)
async def upload_image(
    recipe_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return recipe_service.upload_recipe_image(db, recipe_id, current_user.id, file)

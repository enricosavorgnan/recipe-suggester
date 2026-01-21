from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.category import Category
from app.models.recipe import Recipe


def create_category(db: Session, name: str) -> Category:
    existing = db.query(Category).filter(Category.name == name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists")

    category = Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_categories(db: Session) -> list[Category]:
    return db.query(Category).order_by(Category.created_at.desc()).all()


def update_category(db: Session, category_id: int, new_name: str) -> Category:
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    existing = db.query(Category).filter(Category.name == new_name, Category.id != category_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exists")

    category.name = new_name
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> None:
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    db.delete(category)
    db.commit()


def assign_recipes_to_category(db: Session, recipe_ids: list[int], category_id: int | None, user_id: int) -> list[Recipe]:
    if category_id is not None:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    recipes = db.query(Recipe).filter(Recipe.id.in_(recipe_ids), Recipe.user_id == user_id).all()

    if len(recipes) != len(recipe_ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Some recipes not found")

    for recipe in recipes:
        recipe.category_id = category_id

    db.commit()
    for recipe in recipes:
        db.refresh(recipe)

    return recipes

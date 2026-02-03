from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class JobStatus(str, enum.Enum):
    running = "running"
    completed = "completed"
    failed = "failed"


# represents sync job done by the ML service
class IngredientsJob(Base):
    __tablename__ = "ingredients_jobs"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    status = Column(SQLEnum(JobStatus), nullable=False, default=JobStatus.running)
    ingredients_json = Column(Text, nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)

    recipe = relationship("Recipe", back_populates="ingredients_job")


# represents job called for LLM recipe generation
class RecipeJob(Base):
    __tablename__ = "recipe_jobs"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    status = Column(SQLEnum(JobStatus), nullable=False, default=JobStatus.running)
    recipe_json = Column(Text, nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)

    recipe = relationship("Recipe", back_populates="recipe_job")

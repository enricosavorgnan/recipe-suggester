from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.database import Base


class AuthProvider(str, enum.Enum):
    """Authentication provider options"""
    email = "email"
    google = "google"


class User(Base):
    """
    Core user model - stores basic user information
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship to auth details
    auth = relationship("UserAuth", back_populates="user", uselist=False, cascade="all, delete-orphan")
    recipes = relationship("Recipe", back_populates="user", cascade="all, delete-orphan")


class UserAuth(Base):
    """
    User authentication model - stores auth-specific data (1:1 with User)
    Separates authentication concerns from core user data
    """
    __tablename__ = "user_auth"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Authentication provider (email or google)
    provider = Column(SQLEnum(AuthProvider), nullable=False, default=AuthProvider.email)

    # For email auth: hashed password (null for OAuth users)
    hashed_password = Column(String, nullable=True)

    # For OAuth: provider user ID (null for email users)
    provider_user_id = Column(String, nullable=True, index=True)

    last_login = Column(DateTime, nullable=True)
    is_active = Column(Integer, default=1, nullable=False)  # 1 = active, 0 = disabled

    user = relationship("User", back_populates="auth")

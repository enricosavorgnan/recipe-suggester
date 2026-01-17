from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Annotated
from app.db.database import get_db
from app.models.user import User
from app.utils.security import decode_access_token

# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    this is used in protected endpoints that require authentication.

    Usage:
        @app.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id}

    Args:
        credentials: Bearer token from Authorization header
        db: Database session

    Returns:
        Current authenticated User object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID from token
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if user.auth and user.auth.is_active == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to ensure user is active.
    (It's a redundant check since get_current_user already checks, but kept for clarity)

    Args:
        current_user: User from get_current_user dependency

    Returns:
        Active User object
    """
    return current_user


# Annotated types for cleaner endpoint signatures
# just for cleaner "decorator-like" syntax
RequireAuth = Annotated[User, Depends(get_current_user)]
OptionalAuth = Annotated[User | None, Depends(get_current_user)]

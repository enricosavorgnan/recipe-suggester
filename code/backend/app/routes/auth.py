from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.auth import (
    UserSignupRequest,
    UserLoginRequest,
    GoogleAuthRequest,
    TokenResponse,
    UserResponse,
    GoogleAuthURLResponse
)
from app.services import auth_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(request: UserSignupRequest, db: Session = Depends(get_db)):
    """
    Create a new user account with email and password.

    - **email**: Valid email address (must be unique)
    - **password**: At least 8 characters
    - **full_name**: Optional user's full name

    Returns JWT access token and user data.
    """
    user, access_token = auth_service.signup_with_email(db, request)

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password.

    - **email**: Registered email address
    - **password**: User's password

    Returns JWT access token and user data.
    """
    user, access_token = auth_service.login_with_email(db, request)

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/google", response_model=GoogleAuthURLResponse)
def google_auth():
    """
    Get Google OAuth authorization URL.

    Redirect the user to this URL to start Google authentication flow.
    After user authorizes, Google will redirect back to /auth/google/callback.
    """
    authorization_url = auth_service.get_google_auth_url()
    return GoogleAuthURLResponse(authorization_url=authorization_url)


@router.post("/google/callback", response_model=TokenResponse)
async def google_callback(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """
    Handle Google OAuth callback.

    - **code**: Authorization code received from Google

    Creates new user if doesn't exist, or logs in existing user.
    Returns JWT access token and user data.
    """
    user, access_token = await auth_service.handle_google_callback(db, request.code)

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information.

    Requires valid JWT token in Authorization header:
    Authorization: Bearer <token>

    Returns user data.
    """
    return UserResponse.model_validate(current_user)

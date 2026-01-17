from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from authlib.integrations.starlette_client import OAuth
from app.models.user import User, UserAuth, AuthProvider
from app.schemas.auth import UserSignupRequest, UserLoginRequest
from app.utils.security import hash_password, verify_password, create_access_token
from app.config.settings import settings

# OAuth client for Google
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)


def signup_with_email(db: Session, request: UserSignupRequest) -> tuple[User, str]:
    """
    Create a new user with email and password

    Args:
        db: Database session
        request: Signup request with email, password, full_name

    Returns:
        Tuple of (User, access_token)

    Raises:
        HTTPException: If email already exists
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = User(
        email=request.email,
        full_name=request.full_name
    )
    db.add(user)
    db.flush()  # Get user.id without committing

    # Create auth record
    user_auth = UserAuth(
        user_id=user.id,
        provider=AuthProvider.email,
        hashed_password=hash_password(request.password),
        is_active=1
    )
    db.add(user_auth)
    db.commit()
    db.refresh(user)

    # Generate JWT token
    access_token = create_access_token(data={"sub": str(user.id)})

    return user, access_token


def login_with_email(db: Session, request: UserLoginRequest) -> tuple[User, str]:
    """
    Authenticate user with email and password

    Args:
        db: Database session
        request: Login request with email and password

    Returns:
        Tuple of (User, access_token)

    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not user.auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Check if user uses email auth
    if user.auth.provider != AuthProvider.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This account uses {user.auth.provider.value} authentication"
        )

    # Verify password
    if not verify_password(request.password, user.auth.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Check if account is active
    if user.auth.is_active == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    # Update last login
    user.auth.last_login = datetime.utcnow()
    db.commit()

    # Generate JWT token
    access_token = create_access_token(data={"sub": str(user.id)})

    return user, access_token


def get_google_auth_url() -> str:
    """
    Generate Google OAuth authorization URL

    Returns:
        Authorization URL to redirect user to
    """
    redirect_uri = f"{settings.API_URL}/auth/google/callback"
    authorization_url = oauth.google.authorize_redirect_url(redirect_uri)
    return authorization_url


async def handle_google_callback(db: Session, code: str) -> tuple[User, str]:
    """
    Handle Google OAuth callback and create/login user

    Args:
        db: Database session
        code: Authorization code from Google

    Returns:
        Tuple of (User, access_token)

    Raises:
        HTTPException: If OAuth fails
    """
    try:
        # Exchange code for token
        redirect_uri = f"{settings.API_URL}/auth/google/callback"
        token = await oauth.google.authorize_access_token(code=code, redirect_uri=redirect_uri)

        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google"
            )

        email = user_info.get('email')
        google_user_id = user_info.get('sub')
        full_name = user_info.get('name')

        # Check if user exists
        user = db.query(User).filter(User.email == email).first()

        if user:
            # Existing user - verify it's a Google account
            if user.auth.provider != AuthProvider.google:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"This email is registered with {user.auth.provider.value} authentication"
                )

            # Update last login
            user.auth.last_login = datetime.utcnow()
            db.commit()
        else:
            # New user - create account
            user = User(
                email=email,
                full_name=full_name
            )
            db.add(user)
            db.flush()

            user_auth = UserAuth(
                user_id=user.id,
                provider=AuthProvider.google,
                provider_user_id=google_user_id,
                is_active=1,
                last_login=datetime.utcnow()
            )
            db.add(user_auth)
            db.commit()
            db.refresh(user)

        # Generate JWT token
        access_token = create_access_token(data={"sub": str(user.id)})

        return user, access_token

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authentication failed: {str(e)}"
        )

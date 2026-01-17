"""
Tests for authentication endpoints
"""
import pytest
from fastapi import status


class TestSignup:
    """Tests for /auth/signup endpoint"""

    def test_signup_success(self, client, test_user_data):
        """Test successful user signup"""
        response = client.post("/auth/signup", json=test_user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Check response structure
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

        # Check user data
        user = data["user"]
        assert user["email"] == test_user_data["email"]
        assert user["full_name"] == test_user_data["full_name"]
        assert "id" in user
        assert "created_at" in user

        # Password should not be in response
        assert "password" not in user
        assert "hashed_password" not in user

    def test_signup_duplicate_email(self, client, test_user_data, create_user):
        """Test signup with already registered email"""
        response = client.post("/auth/signup", json=test_user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()

    def test_signup_invalid_email(self, client):
        """Test signup with invalid email format"""
        response = client.post("/auth/signup", json={
            "email": "not-an-email",
            "password": "password123",
            "full_name": "Test"
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_signup_short_password(self, client):
        """Test signup with password < 8 characters"""
        response = client.post("/auth/signup", json={
            "email": "test@example.com",
            "password": "short",
            "full_name": "Test"
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_signup_missing_fields(self, client):
        """Test signup with missing required fields"""
        response = client.post("/auth/signup", json={
            "email": "test@example.com"
            # Missing password
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_signup_without_full_name(self, client):
        """Test signup without optional full_name"""
        response = client.post("/auth/signup", json={
            "email": "test@example.com",
            "password": "password123"
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["user"]["full_name"] is None


class TestLogin:
    """Tests for /auth/login endpoint"""

    def test_login_success(self, client, test_user_data, create_user):
        """Test successful login"""
        response = client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == test_user_data["email"]

    def test_login_wrong_password(self, client, test_user_data, create_user):
        """Test login with incorrect password"""
        response = client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": "wrongpassword"
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client):
        """Test login with email that doesn't exist"""
        response = client.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password123"
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_fields(self, client):
        """Test login with missing fields"""
        response = client.post("/auth/login", json={
            "email": "test@example.com"
            # Missing password
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestProtectedEndpoints:
    """Tests for protected endpoints requiring authentication"""

    def test_get_me_success(self, client, create_user):
        """Test /auth/me with valid token"""
        user, password, token = create_user

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == user.id
        assert data["email"] == user.email
        assert data["full_name"] == user.full_name

    def test_get_me_no_token(self, client):
        """Test /auth/me without token"""
        response = client.get("/auth/me")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_me_invalid_token(self, client):
        """Test /auth/me with invalid token"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_me_malformed_header(self, client):
        """Test /auth/me with malformed Authorization header"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "invalid_format"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestTokenValidation:
    """Tests for JWT token validation"""

    def test_token_contains_user_id(self, client, test_user_data):
        """Test that JWT token contains user ID"""
        from app.utils.security import decode_access_token

        # Signup to get token
        response = client.post("/auth/signup", json=test_user_data)
        token = response.json()["access_token"]

        # Decode and verify
        payload = decode_access_token(token)
        assert payload is not None
        assert "sub" in payload
        # JWT standard uses string for sub
        assert isinstance(payload["sub"], str)
        assert int(payload["sub"]) > 0

    def test_expired_token(self, client, create_user):
        """Test that expired tokens are rejected"""
        from datetime import timedelta
        from app.utils.security import create_access_token

        user, password, _ = create_user

        # Create token that expires immediately
        expired_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(seconds=-1)
        )

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestPasswordSecurity:
    """Tests for password hashing and security"""

    def test_password_is_hashed(self, db_session, test_user_data):
        """Test that passwords are stored as hashes, not plaintext"""
        from app.services.auth_service import signup_with_email
        from app.schemas.auth import UserSignupRequest

        request = UserSignupRequest(**test_user_data)
        user, token = signup_with_email(db_session, request)

        # Password should be hashed
        assert user.auth.hashed_password != test_user_data["password"]
        # bcrypt hash starts with $2a$, $2b$, or $2y$
        assert user.auth.hashed_password.startswith("$2")

    def test_password_verification(self, db_session, test_user_data):
        """Test password verification works correctly"""
        from app.utils.security import hash_password, verify_password

        password = test_user_data["password"]
        hashed = hash_password(password)

        # Correct password should verify
        assert verify_password(password, hashed) is True

        # Wrong password should not verify
        assert verify_password("wrongpassword", hashed) is False

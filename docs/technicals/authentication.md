# Authentication Technical Guide

## Overview

Email + Google OAuth authentication using JWT tokens. Database uses Alembic migrations.

## Database Schema

**users**: id, email, full_name, created_at, updated_at
**user_auth** (1:1): user_id, provider (email or google), hashed_password, provider_user_id, last_login, is_active

## API Endpoints

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/auth/signup` | POST | No | Create account (email/password) |
| `/auth/login` | POST | No | Login (email/password) |
| `/auth/google` | GET | No | Get Google OAuth URL |
| `/auth/google/callback` | POST | No | Handle Google OAuth |
| `/auth/me` | GET | Yes | Get current user |

## Protecting Endpoints

```python
from app.dependencies.auth import RequireAuth

@router.post("/recipes")
def create_recipe(data: dict, current_user: RequireAuth):
    # current_user = authenticated User object
    # current_user.id, .email, .full_name
    pass
```

No auth required = don't add `current_user` parameter.

## Database Migrations

### Setup (First Time)
```bash
cd code/backend
alembic upgrade head
```

### Adding New Field
```bash
# 1. Modify model in app/models/
# 2. Generate migration
alembic revision --autogenerate -m "add field name"

# 3. Review migration in migrations/versions/
# 4. Apply migration
alembic upgrade head
```

### Docker Deployment
Migrations run automatically via Dockerfile CMD:
```dockerfile
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0
```

Or run manually after pulling images:
```bash
docker-compose run backend alembic upgrade head
docker-compose up -d
```

### Common Commands
```bash
alembic current              # Show current revision
alembic history              # Show all migrations
alembic downgrade -1         # Rollback one migration
alembic upgrade head         # Apply all migrations
```

## Google OAuth Setup
(To be done just once)
1. **Google Cloud Console** → Create project
2. **OAuth consent screen** → External → Add scopes: email, profile, openid
3. **Credentials** → Create OAuth client ID → Web application
4. **Authorized redirect URIs**: `http://localhost:8000/auth/google/callback`
5. Copy **Client ID** and **Client Secret** to `.env`:
   ```bash
   GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-secret
   ```

## Configuration (.env)

```bash
# Required
SECRET_KEY=your-secret-32-chars    # Generate: openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=180

# Optional (for Google OAuth)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app
```

**Test user:**
```bash
# Signup
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password123"}'

# Use token
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer <token>"
```

## Migration Workflow

### Local Development
1. Make model changes in `app/models/`
2. `alembic revision --autogenerate -m "description"`
3. Review generated migration
4. `alembic upgrade head`
5. Test changes

### After PR Merge
1. CI builds new Docker image with migration files
2. CD pushes image to registry
3. Pull and restart:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```
4. Migrations run automatically on container start (configured in Dockerfile)

## Security

- Passwords: bcrypt hashing
- Tokens: JWT with HS256, 3-hour expiry
- OAuth: Google OpenID Connect
- HTTPS required in production

## Future Fields Example

```python
# 1. Edit app/models/user.py
class User(Base):
    # ... existing fields ...
    phone_number = Column(String, nullable=True)  # NEW

# 2. Generate migration
alembic revision --autogenerate -m "add user phone number"

# 3. Apply
alembic upgrade head
```


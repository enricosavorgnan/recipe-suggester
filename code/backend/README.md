# Recipe Suggester Backend

FastAPI backend for the Recipe Suggester application. Provides REST API endpoints for recipe management, ingredient detection (relying on ML service), and recipe generation using OpenAI's GPT.

## Table of Contents

- [Project Structure](#project-structure)
- [Design Overview](#design-overview)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config/
│   │   ├── settings.py         # Environment variables configuration
│   │   └── prompts.py          # LLM prompts for recipe generation
│   ├── db/
│   │   └── database.py         # Database connection and session
│   ├── models/                 # SQLAlchemy database models
│   │   ├── user.py
│   │   ├── recipe.py
│   │   ├── job.py            
│   │   └── category.py
│   ├── routes/                 # API route handlers
│   │   ├── auth.py
│   │   ├── recipes.py
│   │   ├── jobs.py
│   │   └── categories.py
│   ├── schemas/                # Pydantic request/response models
│   ├── services/               # Business logic layer
│   │   ├── llm_service.py     # OpenAI integration
│   │   ├── ml_service.py      # ML model integration
│   │   └── job_service.py     # Background job processing
│   └── dependencies/           # FastAPI dependencies (auth, etc.)
├── migrations/                    # Database migrations
├── uploads/                    # User-uploaded images
├── requirements.txt
├── .env.example
└── README.md
```

## Design Overview

### Architecture

The backend follows a layered architecture:
- **Routes**: Handle HTTP requests/responses
- **Services**: Contain business logic and external integrations
- **Models**: Define database schema
- **Schemas**: Validate request/response data

Configuration is **purely environment-variable driven**, no environment-specific code paths. The same codebase works in local development and production.

### Job System Design

The application uses an **asynchronous job system** for long-running ML and LLM operations:

#### Why Jobs?
ML inference and LLM API calls can take several seconds. Instead of blocking HTTP requests, we:
1. Create a job record immediately (status: `running`)
2. Return the job ID to the client
3. Process the operation in the background
4. Update the job status when complete (`completed` or `failed`)
5. Client polls the job endpoint to check progress

#### Job Types

**IngredientsJob**
- Detects ingredients from uploaded recipe images using ML
- Links to a `Recipe` via `recipe_id`
- Stores detected ingredients as JSON (with confidence scores)
- Status flow: `running` → `completed` | `failed`

**RecipeJob**
- Generates recipe instructions from ingredients using LLM
- Links to a `Recipe` via `recipe_id`
- Stores generated recipe as JSON
- Status flow: `running` → `completed` | `failed`

#### Job Processing Flow

```
Client uploads image → Recipe created → IngredientsJob starts
                                              ↓
                                    ML processes image (background)
                                              ↓
                                    Job status → completed
                                              ↓
Client confirms ingredients → RecipeJob starts
                                              ↓
                                    LLM generates recipe (background)
                                              ↓
                                    Job status → completed
```

Each job tracks:
- `start_time`: When the job was created
- `end_time`: When processing finished
- `status`: Current state (running/completed/failed)
- Result JSON: Ingredients or recipe data

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL database running locally or via Docker
- OpenAI API key (for recipe generation)

### Installation

1. **Clone and navigate to backend directory**
   ```bash
   cd code/backend
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**

   Create `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and configure required variables (see [Configuration](#configuration) section).

5. **Set up database**

   Make sure PostgreSQL is running, then run migrations:
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## Configuration

All configuration is managed through environment variables in the `.env` file.

### Required Configuration

These variables **must** be set for the application to work:

#### Database
```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_SERVER=localhost        # Use 'postgres' in Docker
POSTGRES_PORT=5432
POSTGRES_DB=recipe_suggester
```

#### Authentication
```bash
# Generate with: openssl rand -hex 32
SECRET_KEY=your-secret-key-min-32-chars
```

#### OpenAI (for recipe generation)
```bash
OPENAI_API_KEY=sk-proj-...       # Your OpenAI API key
OPENAI_MODEL=gpt-4o-mini         # Model to use (default: gpt-4o-mini)
```

### Optional Configuration

#### CORS
```bash
FRONTEND_URL=http://localhost:3000                    # Primary frontend origin
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3001  # Additional origins
```

#### Google OAuth (optional)
```bash
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

#### API Settings
```bash
API_URL=http://localhost:8000    # Backend URL (for callbacks)
DEBUG=True                        # Enable debug mode
```

### Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `POSTGRES_SERVER` | Database host | Yes | `localhost` |
| `POSTGRES_USER` | Database username | Yes | `postgres` |
| `POSTGRES_PASSWORD` | Database password | Yes | `postgres` |
| `POSTGRES_PORT` | Database port | Yes | `5432` |
| `POSTGRES_DB` | Database name | Yes | `recipe_suggester` |
| `SECRET_KEY` | JWT secret key | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `OPENAI_MODEL` | OpenAI model name | No | `gpt-4o-mini` |
| `FRONTEND_URL` | Frontend URL for CORS | No | `http://localhost:3000` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | No | - |
| `GOOGLE_CLIENT_SECRET` | Google OAuth secret | No | - |
| `DEBUG` | Enable debug mode | No | `True` |
| `API_URL` | Backend base URL | No | `http://localhost:8000` |

See `.env.example` for the complete list.

## API Documentation

Interactive API documentation is automatically generated:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /recipes` - List user's recipes
- `POST /recipes` - Create new recipe
- `POST /recipes/{id}/upload` - Upload recipe image
- `POST /jobs/ingredients/{recipe_id}` - Start ingredient detection
- `GET /jobs/ingredients/{job_id}` - Check ingredient detection status
- `POST /jobs/recipe/{recipe_id}` - Start recipe generation
- `GET /jobs/recipe/{job_id}` - Check recipe generation status
- `GET /jobs/by-recipe/{recipe_id}` - Get all jobs for a recipe

## Contributing


### Database Migrations

When you modify database models, create a new migration:

```bash
# Generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Apply migration
alembic upgrade head
```

**Common migration commands:**
```bash
alembic current              # Show current migration version
alembic history              # Show all migrations
alembic downgrade -1         # Rollback one migration
alembic upgrade head         # Apply all pending migrations
```

### Project Architecture

- **Keep routes thin**: Routes should only handle HTTP concerns (validation, response formatting)
- **Business logic in services**: All business logic, external API calls, and complex operations go in service modules
- **Database operations in services**: Services interact with database models
- **Type hints everywhere**: Use Python type hints for better IDE support and catching bugs
- **Async where appropriate**: Use async/await for I/O operations (database, external APIs)

### Adding a New Feature

1. Define database model in `app/models/` (if needed)
2. Create migration with `alembic revision --autogenerate`
3. Define request/response schemas in `app/schemas/`
4. Implement business logic in `app/services/`
5. Create route handlers in `app/routes/`
6. Test with Swagger UI at `/docs`

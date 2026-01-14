# Recipe Suggester Backend

FastAPI backend for the Recipe Suggester application.

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config/
│   │   └── settings.py      # Environment-aware settings
│   ├── db/
│   │   └── database.py      # Database connection
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # API routes
│   └── services/            # Business logic
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Environment Configuration

This project supports three environments:
- **local**: Local development (services on localhost)
- **docker**: Docker Compose deployment (services use container names)
- **production**: Production deployment

Configure via `ENVIRONMENT` variable in `.env` file.

## Setup

### 1. Create `.env` file

```bash
cp .env.example .env
```

### 2. Configure environment variables

Edit `.env` and set `ENVIRONMENT`:

**For local development:**
```bash
ENVIRONMENT=local
POSTGRES_SERVER=localhost
```

**For Docker deployment:**
```bash
ENVIRONMENT=docker
POSTGRES_SERVER=postgres
```

## Running Locally

### Prerequisites
- Python 3.11+
- PostgreSQL (running on localhost:5432)

### Steps

1. Create and activate virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure `.env` has `ENVIRONMENT=local`

4. Start the server:
```bash
uvicorn app.main:app --reload
```

API available at: `http://localhost:8000`

## Running with Docker Compose

### Prerequisites
- Docker
- Docker Compose

### Steps

1. Ensure `.env` has `ENVIRONMENT=docker`

2. Build and start services:
```bash
docker-compose up --build
```

This starts:
- PostgreSQL on port 5432
- Backend API on port 8000

3. Stop services:
```bash
docker-compose down
```

4. Stop and remove volumes:
```bash
docker-compose down -v
```

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Key Environment Variables

| Variable | Description | Local | Docker |
|----------|-------------|-------|--------|
| `ENVIRONMENT` | Environment type | `local` | `docker` |
| `POSTGRES_SERVER` | Database host | `localhost` | `postgres` |
| `FRONTEND_URL` | CORS origin | `http://localhost:3000` | `http://localhost:3000` |
| `DEBUG` | Debug mode | `True` | `True` |

See `.env.example` for all variables.

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
├── requirements.txt
├── .env.example
└── README.md
```

## Configuration

Configuration is driven purely by environment variables in `.env`.
No environment-specific code paths - just change env vars.

## Setup

Create `.env` file:

```bash
cp .env.example .env
```

Default values are configured for local development.

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

3. Start the server:
```bash
uvicorn app.main:app --reload
```

API available at: `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Key Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_SERVER` | Database host | `localhost` |
| `FRONTEND_URL` | CORS origin | `http://localhost:3000` |
| `DEBUG` | Debug mode | `True` |
| `API_URL` | Backend URL | `http://localhost:8000` |

See `.env.example` for all variables.

## Architecture Notes

- Configuration is purely env-var driven
- No environment-specific code paths
- Same code works in local dev and deployed containers

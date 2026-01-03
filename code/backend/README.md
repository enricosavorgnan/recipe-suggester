# Recipe Suggester Backend

FastAPI backend for the Recipe Suggester application.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py      # Application settings
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py      # Database connection setup
│   ├── models/              # SQLAlchemy models
│   │   └── __init__.py
│   ├── routes/              # API routes
│   │   ├── __init__.py
│   │   └── health.py        # Health check endpoints
│   └── services/            # Business logic
│       └── __init__.py
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```

4. Update the `.env` file with PostgreSQL credentials (for now just initialization, we don't do that immediately)

## Running the Application

Run the FastAPI application with uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint
- `GET /health/db` - Database health check endpoint

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from sqlalchemy import text

router = APIRouter()


@router.get("/health")
def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {
        "status": "healthy",
        "message": "Recipe Suggester API is running"
    }


@router.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify database connectivity.
    """
    try:
        # Try to execute a simple query
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "message": "Database connection is working"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }

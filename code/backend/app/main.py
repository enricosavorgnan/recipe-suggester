from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config.settings import settings
from app.routes import health, auth, recipes, categories, jobs
from pathlib import Path

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for Recipe Suggester application",
    version=settings.API_VERSION,
    debug=settings.DEBUG
)

# CORS middleware configuration - environment-aware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(auth.router)
app.include_router(recipes.router)
app.include_router(categories.router)
app.include_router(jobs.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Recipe Suggester API",
        "version": settings.API_VERSION
    }

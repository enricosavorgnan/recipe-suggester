from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.routes import health

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

# Include routers
app.include_router(health.router, tags=["health"])


@app.get("/")
def root():
    return {
        "message": "Welcome to Recipe Suggester API",
        "environment": settings.ENVIRONMENT,
        "version": settings.API_VERSION
    }

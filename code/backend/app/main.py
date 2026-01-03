from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import health

app = FastAPI(
    title="Recipe Suggester API",
    description="Backend API for Recipe Suggester application",
    version="0.1.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])

@app.get("/")
def root():
    return {"message": "Welcome to Recipe Suggester API"}

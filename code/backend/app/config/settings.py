from pydantic_settings import BaseSettings
from typing import Literal, Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Supports multiple environments: local, docker, production
    """

    # Environment configuration
    ENVIRONMENT: Literal["local", "docker", "production"] = "local"

    # Application settings
    APP_NAME: str = "Recipe Suggester API"
    DEBUG: bool = True
    API_VERSION: str = "0.1.0"

    # Database settings
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "recipe_suggester"

    # CORS settings
    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_ORIGINS: Optional[str] = None

    # API settings
    API_URL: str = "http://localhost:8000"

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from environment variables"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def CORS_ORIGINS(self) -> list[str]:
        """
        Get list of allowed CORS origins based on environment.
        Always includes FRONTEND_URL, plus any additional origins from ALLOWED_ORIGINS.
        """
        origins = [self.FRONTEND_URL]

        if self.ALLOWED_ORIGINS:
            additional_origins = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
            origins.extend(additional_origins)

        return origins

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT == "production"

    @property
    def is_docker(self) -> bool:
        """Check if running in Docker environment"""
        return self.ENVIRONMENT == "docker"

    @property
    def is_local(self) -> bool:
        """Check if running in local development environment"""
        return self.ENVIRONMENT == "local"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

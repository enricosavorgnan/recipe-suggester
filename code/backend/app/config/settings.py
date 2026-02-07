from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Configuration is driven purely by env vars, not by environment type.
    Works identically in local dev (uvicorn) and deployed (docker).
    """

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

    # Authentication settings
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Google OAuth settings
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # OpenAI settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Models service settings
    MODELS_SERVICE_URL: str = "http://localhost:8001"

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from environment variables"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def CORS_ORIGINS(self) -> list[str]:
        """
        Get list of allowed CORS origins.
        Always includes FRONTEND_URL, plus any additional origins from ALLOWED_ORIGINS.
        """
        origins = [self.FRONTEND_URL]

        if self.ALLOWED_ORIGINS:
            additional_origins = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
            origins.extend(additional_origins)

        return origins

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

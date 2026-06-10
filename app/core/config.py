from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    DATABASE_URL: str
    API_KEY: str
    GEMINI_API_KEY: str = "missing"
    GEMINI_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = Field(default=500, ge=50)
    CHUNK_OVERLAP: int = Field(default=50, ge=0)
    TOP_K: int = Field(default=5, ge=1)
    MAX_UPLOAD_SIZE_MB: int = Field(default=10, ge=1)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]

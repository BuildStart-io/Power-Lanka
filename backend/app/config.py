from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Gemini
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-flash-lite-latest"
    gemini_embedding_model: str = "text-embedding-004"

    # OpenRouter
    openrouter_api_key: str | None = None
    openrouter_model: str = "google/gemini-2.0-flash-001"

    # Qdrant
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection_name: str = "rag_products"

    # App
    upload_dir: str = "uploads"
    data_dir: str = "data"
    max_file_size_mb: int = 5

    # WASender Configuration
    wasender_api_url: str = "https://www.wasenderapi.com/api/send-message"
    whatsapp_api_bearer_token: str | None = None

    # RAG Settings
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_results: int = 5

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

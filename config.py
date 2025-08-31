# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM provider / keys
    LLM_PROVIDER: str = "openai"   # "openai" or "gemini"
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "models/gemini-1.5-pro"

    # Vector store backend: "faiss" or "chroma"
    VS_BACKEND: str = "faiss"

    # Paths
    DB_PATH: str = "data/Northwind_small.sqlite"
    DOCS_DIR: str = "data/docs"
    VS_DIR: str = "data/vectorstore"

    # Retriever settings
    RETRIEVAL_K: int = 50

    class Config:
        env_file = ".env"

settings = Settings()

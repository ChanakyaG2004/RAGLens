"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for RAGLens.

    Local models are the default. Setting ``USE_OPENAI=true`` explicitly opts into
    the OpenAI embedding and chat providers.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://raglens:raglens@localhost:5432/raglens"

    local_llm_mode: bool = True
    use_openai: bool = False

    local_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    chunk_size: int = 900
    chunk_overlap: int = 150
    top_k: int = 5

    @property
    def embedding_dimensions(self) -> int:
        """Return the vector dimension emitted by the active embedding provider."""
        return 1536 if self.use_openai else 384


@lru_cache
def get_settings() -> Settings:
    """Return one shared settings instance for the process."""
    return Settings()

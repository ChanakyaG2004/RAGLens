"""Embedding providers for local sentence-transformers and optional OpenAI."""

from functools import lru_cache

from openai import OpenAI

from ..config import get_settings


class EmbeddingError(RuntimeError):
    """Raised when the configured embedding provider is unavailable."""


@lru_cache
def _local_embedder():
    """Load and cache the local MiniLM embedding model once per process."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise EmbeddingError(
            "Local embeddings require sentence-transformers. Run: pip install -r requirements.txt"
        ) from exc

    settings = get_settings()
    try:
        return SentenceTransformer(settings.local_embedding_model)
    except Exception as exc:
        raise EmbeddingError(
            f"Could not load local embedding model '{settings.local_embedding_model}'. "
            "Check the model download and Hugging Face connectivity."
        ) from exc


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of text using the active provider."""
    settings = get_settings()

    if settings.use_openai:
        if not settings.openai_api_key:
            raise EmbeddingError("USE_OPENAI=true requires OPENAI_API_KEY")

        client = OpenAI(api_key=settings.openai_api_key)
        response = client.embeddings.create(model=settings.embedding_model, input=texts)
        return [item.embedding for item in response.data]

    if not settings.local_llm_mode:
        raise EmbeddingError("Enable LOCAL_LLM_MODE=true or USE_OPENAI=true")

    try:
        return _local_embedder().encode(texts, normalize_embeddings=True).tolist()
    except EmbeddingError:
        raise
    except Exception as exc:
        raise EmbeddingError(
            "Local embedding generation failed. Check the sentence-transformers installation."
        ) from exc


def warm_up_embeddings() -> None:
    """Prepare the local model during startup rather than making the first upload wait."""
    settings = get_settings()
    if settings.local_llm_mode and not settings.use_openai:
        _local_embedder()

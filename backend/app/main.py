"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import initialize_database
from .routers import documents, evaluations, questions, traces
from .services.embeddings import EmbeddingError, warm_up_embeddings


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize storage and prepare local models during API startup."""
    initialize_database()
    try:
        warm_up_embeddings()
    except EmbeddingError as exc:
        # The API still starts so upload can return this clear provider error.
        print(f"Local embedding model is not ready: {exc}")
    yield


app = FastAPI(title="RAGLens API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api")
app.include_router(questions.router, prefix="/api")
app.include_router(traces.router, prefix="/api")
app.include_router(evaluations.router, prefix="/api")


@app.get("/api/health")
def health() -> dict[str, str]:
    """Simple liveness endpoint for local development."""
    return {"status": "ok"}

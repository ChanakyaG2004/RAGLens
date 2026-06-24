"""Semantic vector retrieval over indexed document chunks."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Chunk, Document


def retrieve_chunks(db: Session, question_embedding: list[float], limit: int) -> list[dict]:
    """Return the nearest document chunks and a normalized cosine-similarity score."""
    distance = Chunk.embedding.cosine_distance(question_embedding).label("distance")
    statement = (
        select(Chunk, Document, distance)
        .join(Document)
        .order_by(distance)
        .limit(limit)
    )

    return [
        {
            "chunk": chunk,
            "document": document,
            "similarity": max(0.0, 1.0 - float(distance_value)),
        }
        for chunk, document, distance_value in db.execute(statement)
    ]

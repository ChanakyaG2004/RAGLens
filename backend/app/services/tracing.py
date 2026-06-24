"""Persistence helpers for inspectable RAG execution traces."""

from sqlalchemy.orm import Session

from ..models import RetrievedChunk, Trace


def record_trace(
    db: Session,
    question: str,
    prompt: str,
    answer: str,
    model: str,
    results: list[dict],
    timing: dict[str, int],
    scores: dict[str, float] | None = None,
) -> Trace:
    """Save an answer, its evidence snapshots, and stage timing measurements."""
    trace = Trace(
        question=question,
        final_prompt=prompt,
        answer=answer,
        model=model,
        **timing,
        **(scores or {}),
    )
    db.add(trace)
    db.flush()

    for rank, item in enumerate(results, start=1):
        chunk = item["chunk"]
        document = item["document"]
        db.add(
            RetrievedChunk(
                trace_id=trace.id,
                chunk_id=chunk.id,
                rank=rank,
                similarity_score=item["similarity"],
                snapshot={
                    "document": document.filename,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                },
            )
        )

    db.commit()
    db.refresh(trace)
    return trace

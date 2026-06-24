"""Trace inspection endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import Trace
from ..schemas import Citation, EvaluationScores, TraceResponse, TraceTiming

router = APIRouter(prefix="/traces", tags=["traces"])


def serialize_trace(trace: Trace) -> TraceResponse:
    """Map a trace ORM object to its API representation."""
    retrieved_chunks = sorted(trace.retrieved_chunks, key=lambda item: item.rank)
    citations = [
        Citation(
            document=item.snapshot["document"],
            chunk_index=item.snapshot["chunk_index"],
            content=item.snapshot["content"],
            similarity_score=item.similarity_score,
        )
        for item in retrieved_chunks
    ]

    return TraceResponse(
        id=trace.id,
        question=trace.question,
        final_prompt=trace.final_prompt,
        answer=trace.answer,
        model=trace.model,
        created_at=trace.created_at,
        retrieved_chunks=citations,
        timing=TraceTiming(
            embedding_ms=trace.embedding_ms,
            retrieval_ms=trace.retrieval_ms,
            generation_ms=trace.generation_ms,
            total_ms=trace.total_ms,
        ),
        scores=EvaluationScores(
            faithfulness=trace.faithfulness,
            context_relevance=trace.context_relevance,
            citation_support=trace.citation_support,
            hallucination_risk=trace.hallucination_risk,
        ) if trace.faithfulness is not None else None,
    )


@router.get("", response_model=list[TraceResponse])
def list_traces(db: Session = Depends(get_db)):
    """List RAG traces from newest to oldest."""
    statement = (
        select(Trace)
        .options(selectinload(Trace.retrieved_chunks))
        .order_by(Trace.created_at.desc())
    )
    traces = db.scalars(statement).all()
    return [serialize_trace(trace) for trace in traces]


@router.get("/{trace_id}", response_model=TraceResponse)
def get_trace(trace_id: UUID, db: Session = Depends(get_db)):
    """Fetch one complete persisted RAG run."""
    statement = (
        select(Trace)
        .options(selectinload(Trace.retrieved_chunks))
        .where(Trace.id == trace_id)
    )
    trace = db.scalar(statement)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return serialize_trace(trace)

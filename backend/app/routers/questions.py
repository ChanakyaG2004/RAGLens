"""Question answering endpoint and RAG timing instrumentation."""

from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..models import Chunk
from ..schemas import AnswerResponse, Citation, QuestionRequest, TraceTiming
from ..services.embeddings import embed_texts
from ..services.evaluation import score_answer
from ..services.generation import build_prompt, generate_answer
from ..services.retrieval import retrieve_chunks
from ..services.tracing import record_trace

router = APIRouter(prefix="/questions", tags=["questions"])


@router.post("/ask", response_model=AnswerResponse)
def ask_question(payload: QuestionRequest, db: Session = Depends(get_db)):
    """Answer a question from retrieved context and persist a full RAG trace."""
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    chunk_count = db.scalar(select(func.count()).select_from(Chunk))
    if not chunk_count:
        raise HTTPException(status_code=400, detail="Upload at least one document before asking a question")

    settings = get_settings()
    run_started_at = perf_counter()

    try:
        embedding_started_at = perf_counter()
        question_embedding = embed_texts([question])[0]
        embedding_ms = round((perf_counter() - embedding_started_at) * 1000)

        retrieval_started_at = perf_counter()
        results = retrieve_chunks(db, question_embedding, payload.top_k or settings.top_k)
        retrieval_ms = round((perf_counter() - retrieval_started_at) * 1000)

        prompt = build_prompt(question, results)

        generation_started_at = perf_counter()
        answer, model = generate_answer(prompt)
        generation_ms = round((perf_counter() - generation_started_at) * 1000)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    timing = {
        "embedding_ms": embedding_ms,
        "retrieval_ms": retrieval_ms,
        "generation_ms": generation_ms,
        "total_ms": round((perf_counter() - run_started_at) * 1000),
    }
    scores = score_answer(question, answer, results)
    trace = record_trace(db, question, prompt, answer, model, results, timing, scores)
    citations = [
        Citation(
            document=item["document"].filename,
            chunk_index=item["chunk"].chunk_index,
            content=item["chunk"].content,
            similarity_score=item["similarity"],
        )
        for item in results
    ]

    return AnswerResponse(
        trace_id=trace.id,
        answer=answer,
        citations=citations,
        model=model,
        timing=TraceTiming(**timing),
    )

"""Pydantic request and response models for the public API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    chunk_count: int
    created_at: datetime


class QuestionRequest(BaseModel):
    question: str
    top_k: int | None = None


class Citation(BaseModel):
    document: str
    chunk_index: int
    content: str
    similarity_score: float


class TraceTiming(BaseModel):
    embedding_ms: int
    retrieval_ms: int
    generation_ms: int
    total_ms: int


class EvaluationScores(BaseModel):
    faithfulness: float
    context_relevance: float
    citation_support: float
    hallucination_risk: float


class AnswerResponse(BaseModel):
    trace_id: UUID
    answer: str
    citations: list[Citation]
    model: str
    timing: TraceTiming


class TraceResponse(BaseModel):
    id: UUID
    question: str
    final_prompt: str
    answer: str
    model: str
    created_at: datetime
    retrieved_chunks: list[Citation]
    timing: TraceTiming
    scores: EvaluationScores | None = None


class EvaluationCase(BaseModel):
    question: str
    expected_document: str | None = None


class EvaluationRunRequest(BaseModel):
    name: str = "Evaluation run"
    cases: list[EvaluationCase]
    top_k: int | None = None
    chunk_size: int | None = None


class EvaluationCaseResult(BaseModel):
    question: str
    expected_document: str | None
    retrieved_documents: list[str]
    retrieval_hit: bool | None
    answer: str
    scores: EvaluationScores
    total_ms: int


class EvaluationRunResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    config: dict
    averages: EvaluationScores
    retrieval_hit_rate: float | None
    results: list[EvaluationCaseResult]

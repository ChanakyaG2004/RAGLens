"""Persistent data model for documents, vectors, and observable RAG runs."""

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text)
    chunk_index: Mapped[int] = mapped_column(Integer)

    # A dimensionless pgvector column supports local MiniLM (384 dimensions) or
    # OpenAI embeddings (1,536). One database should use one provider at a time.
    embedding: Mapped[list[float]] = mapped_column(Vector())

    document: Mapped[Document] = relationship(back_populates="chunks")


class Trace(Base):
    __tablename__ = "traces"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question: Mapped[str] = mapped_column(Text)
    final_prompt: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    model: Mapped[str] = mapped_column(String(100))

    embedding_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    retrieval_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    generation_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    total_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    faithfulness: Mapped[float | None] = mapped_column(Float, nullable=True)
    context_relevance: Mapped[float | None] = mapped_column(Float, nullable=True)
    citation_support: Mapped[float | None] = mapped_column(Float, nullable=True)
    hallucination_risk: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    retrieved_chunks: Mapped[list["RetrievedChunk"]] = relationship(
        back_populates="trace",
        cascade="all, delete-orphan",
    )


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    config: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    results: Mapped[list["EvaluationResult"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evaluation_runs.id", ondelete="CASCADE"))
    question: Mapped[str] = mapped_column(Text)
    expected_document: Mapped[str | None] = mapped_column(String(255), nullable=True)
    answer: Mapped[str] = mapped_column(Text)
    retrieved_documents: Mapped[dict] = mapped_column(JSONB)
    faithfulness: Mapped[float] = mapped_column(Float)
    context_relevance: Mapped[float] = mapped_column(Float)
    citation_support: Mapped[float] = mapped_column(Float)
    hallucination_risk: Mapped[float] = mapped_column(Float)
    total_ms: Mapped[int] = mapped_column(Integer)
    run: Mapped[EvaluationRun] = relationship(back_populates="results")


class RetrievedChunk(Base):
    __tablename__ = "retrieved_chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("traces.id", ondelete="CASCADE"))
    chunk_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chunks.id"))
    rank: Mapped[int] = mapped_column(Integer)
    similarity_score: Mapped[float] = mapped_column(Float)
    snapshot: Mapped[dict] = mapped_column(JSONB)

    trace: Mapped[Trace] = relationship(back_populates="retrieved_chunks")

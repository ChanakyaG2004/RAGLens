"""Document ingestion endpoints."""

import asyncio

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..models import Chunk, Document
from ..schemas import DocumentResponse
from ..services.chunking import chunk_text
from ..services.document_text import DocumentExtractionError, extract_text
from ..services.embeddings import embed_texts

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Validate, extract, chunk, embed, and persist a supported document."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="A filename is required")

    try:
        content = extract_text(file.filename, await file.read())
    except DocumentExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    settings = get_settings()
    chunks = chunk_text(content, settings.chunk_size, settings.chunk_overlap)
    if not chunks:
        raise HTTPException(status_code=400, detail="The uploaded document has no readable text")

    try:
        embeddings = await asyncio.to_thread(embed_texts, chunks)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    document = Document(filename=file.filename, content=content)
    db.add(document)
    db.flush()

    db.add_all(
        Chunk(
            document_id=document.id,
            content=chunk_content,
            chunk_index=index,
            embedding=embedding,
        )
        for index, (chunk_content, embedding) in enumerate(zip(chunks, embeddings))
    )
    db.commit()
    db.refresh(document)

    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        chunk_count=len(chunks),
        created_at=document.created_at,
    )

"""Evaluation-run APIs for comparable, persisted RAG quality measurements."""

from statistics import mean

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..config import get_settings
from ..database import get_db
from ..models import EvaluationResult, EvaluationRun
from ..schemas import EvaluationCaseResult, EvaluationRunRequest, EvaluationRunResponse, EvaluationScores
from ..services.evaluation import score_answer
from ..services.embeddings import embed_texts
from ..services.generation import build_prompt, generate_answer
from ..services.retrieval import retrieve_chunks

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


def serialize(run: EvaluationRun) -> EvaluationRunResponse:
    results = [EvaluationCaseResult(question=item.question, expected_document=item.expected_document, retrieved_documents=item.retrieved_documents["items"], retrieval_hit=item.retrieved_documents.get("hit"), answer=item.answer, scores=EvaluationScores(faithfulness=item.faithfulness, context_relevance=item.context_relevance, citation_support=item.citation_support, hallucination_risk=item.hallucination_risk), total_ms=item.total_ms) for item in run.results]
    scores = [item.scores for item in results]
    return EvaluationRunResponse(id=run.id, name=run.name, created_at=run.created_at, config=run.config, averages=EvaluationScores(**{key: round(mean(getattr(score, key) for score in scores), 3) for key in EvaluationScores.model_fields}), retrieval_hit_rate=round(mean(item.retrieval_hit for item in results), 3) if results and all(item.retrieval_hit is not None for item in results) else None, results=results)


def get_run(db: Session, run_id):
    run = db.scalar(select(EvaluationRun).options(selectinload(EvaluationRun.results)).where(EvaluationRun.id == run_id))
    if not run:
        raise HTTPException(404, "Evaluation run not found")
    return run


@router.post("/runs", response_model=EvaluationRunResponse)
def create_run(payload: EvaluationRunRequest, db: Session = Depends(get_db)):
    if not payload.cases:
        raise HTTPException(400, "Add at least one evaluation question")
    settings = get_settings()
    config = {"top_k": payload.top_k or settings.top_k, "chunk_size": payload.chunk_size or settings.chunk_size, "provider": "openai" if settings.use_openai else "local", "retrieval": "vector"}
    run = EvaluationRun(name=payload.name, config=config)
    db.add(run); db.flush()
    import time
    for case in payload.cases:
        started = time.perf_counter(); embedding = embed_texts([case.question])[0]; retrieved = retrieve_chunks(db, embedding, config["top_k"]); prompt = build_prompt(case.question, retrieved); answer, _ = generate_answer(prompt); scores = score_answer(case.question, answer, retrieved); documents = [item["document"].filename for item in retrieved]; hit = case.expected_document in documents if case.expected_document else None
        db.add(EvaluationResult(run_id=run.id, question=case.question, expected_document=case.expected_document, answer=answer, retrieved_documents={"items": documents, "hit": hit}, total_ms=round((time.perf_counter() - started) * 1000), **scores))
    db.commit(); db.refresh(run)
    run = db.query(EvaluationRun).options(selectinload(EvaluationRun.results)).filter(EvaluationRun.id == run.id).one()
    return serialize(run)


@router.get("/runs", response_model=list[EvaluationRunResponse])
def list_runs(db: Session = Depends(get_db)):
    runs = db.scalars(select(EvaluationRun).options(selectinload(EvaluationRun.results)).order_by(EvaluationRun.created_at.desc())).all()
    return [serialize(run) for run in runs]


@router.get("/runs/{run_id}", response_model=EvaluationRunResponse)
def get_evaluation_run(run_id, db: Session = Depends(get_db)):
    return serialize(get_run(db, run_id))


@router.get("/runs/{run_id}/report.md", response_class=Response)
def markdown_report(run_id, db: Session = Depends(get_db)):
    run = serialize(get_run(db, run_id))
    lines = [f"# {run.name}", "", "## Summary", "", f"- Faithfulness: {run.averages.faithfulness:.1%}", f"- Context relevance: {run.averages.context_relevance:.1%}", f"- Citation support: {run.averages.citation_support:.1%}", f"- Hallucination risk: {run.averages.hallucination_risk:.1%}", f"- Retrieval hit rate: {run.retrieval_hit_rate:.1%}" if run.retrieval_hit_rate is not None else "- Retrieval hit rate: not labeled", "", "## Cases", ""]
    for result in run.results:
        lines.extend([f"### {result.question}", f"- Expected source: {result.expected_document or 'not labeled'}", f"- Retrieved: {', '.join(result.retrieved_documents)}", f"- Faithfulness: {result.scores.faithfulness:.1%}", f"- Answer: {result.answer}", ""])
    return Response("\n".join(lines), media_type="text/markdown", headers={"Content-Disposition": f'attachment; filename="raglens-{run.id}.md"'})


@router.get("/runs/{run_id}/report.pdf", response_class=Response)
def pdf_report(run_id, db: Session = Depends(get_db)):
    run = serialize(get_run(db, run_id))
    text_lines = [run.name, f"Faithfulness {run.averages.faithfulness:.1%} | Context relevance {run.averages.context_relevance:.1%}", f"Citation support {run.averages.citation_support:.1%} | Hallucination risk {run.averages.hallucination_risk:.1%}"]
    for result in run.results:
        text_lines.append(f"- {result.question[:85]}")
    content = "BT /F1 12 Tf 50 760 Td " + " Tj 0 -20 Td ".join(f"({line.replace('(', '[').replace(')', ']')})" for line in text_lines) + " Tj ET"
    objects = ["<< /Type /Catalog /Pages 2 0 R >>", "<< /Type /Pages /Kids [3 0 R] /Count 1 >>", "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>", "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>", f"<< /Length {len(content)} >>\nstream\n{content}\nendstream"]
    pdf = "%PDF-1.4\n"; offsets = [0]
    for index, obj in enumerate(objects, 1): offsets.append(len(pdf)); pdf += f"{index} 0 obj\n{obj}\nendobj\n"
    xref = len(pdf); pdf += f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n" + "".join(f"{offset:010d} 00000 n \n" for offset in offsets[1:]) + f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF"
    return Response(pdf.encode(), media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="raglens-{run.id}.pdf"'})

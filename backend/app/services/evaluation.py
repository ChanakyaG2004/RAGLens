"""Reproducible, local heuristic scoring for RAG evaluation runs."""

import re

TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]{3,}")
CITATION_PATTERN = re.compile(r"\[Source\s+\d+\]")


def _tokens(text: str) -> set[str]:
    return set(TOKEN_PATTERN.findall(text.lower()))


def score_answer(question: str, answer: str, results: list[dict]) -> dict[str, float]:
    """Return transparent token-overlap scores; these are not LLM-as-a-judge scores."""
    answer_tokens = _tokens(answer)
    question_tokens = _tokens(question)
    context_tokens = _tokens(" ".join(item["chunk"].content for item in results))
    answer_overlap = len(answer_tokens & context_tokens) / max(1, len(answer_tokens))
    question_overlap = len(question_tokens & context_tokens) / max(1, len(question_tokens))
    has_citation = bool(CITATION_PATTERN.search(answer))
    citation_support = 1.0 if has_citation and results else 0.0
    return {
        "faithfulness": round(answer_overlap, 3),
        "context_relevance": round(question_overlap, 3),
        "citation_support": citation_support,
        "hallucination_risk": round(1 - answer_overlap, 3),
    }

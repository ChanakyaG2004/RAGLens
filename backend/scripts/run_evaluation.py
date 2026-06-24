"""Run a small reproducible retrieval and citation evaluation against RAGLens.

Start the API and upload the evaluation source before running this script:
    python scripts/run_evaluation.py
"""

import json
import re
from pathlib import Path
from statistics import mean
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_URL = "http://localhost:8000/api/questions/ask"
DATASET_PATH = Path(__file__).resolve().parents[2] / "evaluation" / "raglens_eval.json"


def ask(question: str) -> dict:
    request = Request(
        API_URL,
        data=json.dumps({"question": question}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=180) as response:
        return json.loads(response.read().decode())


def main() -> None:
    cases = json.loads(DATASET_PATH.read_text())
    results = []
    for case in cases:
        response = ask(case["question"])
        retrieved_documents = {citation["document"] for citation in response["citations"]}
        results.append({
            "question": case["question"],
            "expected_document": case["expected_document"],
            "retrieval_hit": case["expected_document"] in retrieved_documents,
            "has_inline_citation": bool(re.search(r"\[Source\s+\d+\]", response["answer"])),
            "total_latency_ms": response["timing"]["total_ms"],
        })
    summary = {
        "cases": len(results),
        "retrieval_hit_rate_at_k": round(mean(result["retrieval_hit"] for result in results), 3),
        "answers_with_inline_citations_rate": round(mean(result["has_inline_citation"] for result in results), 3),
        "average_total_latency_ms": round(mean(result["total_latency_ms"] for result in results)),
        "results": results,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    try:
        main()
    except HTTPError as error:
        detail = error.read().decode()
        raise SystemExit(f"Evaluation failed ({error.code}): {detail}") from error
    except URLError as error:
        raise SystemExit("Evaluation could not reach the API. Start the FastAPI server on port 8000.") from error

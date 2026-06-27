"""Run a reproducible RAGLens evaluation benchmark.

Start the API and upload the evaluation corpus before running this script:
    python scripts/run_evaluation.py
"""

import argparse
import json
import re
from pathlib import Path
from statistics import mean
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_URL = "http://localhost:8000/api/evaluations/runs"
DEFAULT_DATASET_PATH = Path(__file__).resolve().parents[2] / "evaluation" / "raglens_eval_25.json"
CITATION_PATTERN = re.compile(r"\[Source\s+\d+\]")


def normalize_case(case: dict) -> dict:
    return {
        "question": case["question"],
        "expected_document": case.get("expected_document") or case.get("expected_source_document"),
    }


def create_run(cases: list[dict], top_k: int, name: str) -> dict:
    payload = {
        "name": name,
        "top_k": top_k,
        "cases": [normalize_case(case) for case in cases],
    }
    request = Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=900) as response:
        return json.loads(response.read().decode())


def average(items: list[float | int | bool]) -> float:
    return round(mean(items), 3)


def summarize_run(run: dict) -> dict:
    results = run["results"]
    return {
        "run_id": run["id"],
        "retrieval_hit_rate": run["retrieval_hit_rate"],
        "citation_coverage": average([bool(CITATION_PATTERN.search(item["answer"])) for item in results]),
        "average_total_latency_ms": round(mean(item["total_ms"] for item in results)),
        "average_faithfulness": run["averages"]["faithfulness"],
        "average_context_relevance": run["averages"]["context_relevance"],
        "average_hallucination_risk": run["averages"]["hallucination_risk"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the RAGLens benchmark at top_k=3 and top_k=5.")
    parser.add_argument(
        "--dataset",
        default=DEFAULT_DATASET_PATH,
        type=Path,
        help="Path to a JSON evaluation dataset.",
    )
    args = parser.parse_args()

    cases = json.loads(args.dataset.read_text())
    run_at_3 = create_run(cases, top_k=3, name=f"{args.dataset.stem} Hit@3")
    run_at_5 = create_run(cases, top_k=5, name=f"{args.dataset.stem} Hit@5")
    summary_at_3 = summarize_run(run_at_3)
    summary_at_5 = summarize_run(run_at_5)

    summary = {
        "dataset": str(args.dataset),
        "cases": len(cases),
        "retrieval_hit_rate_at_3": summary_at_3["retrieval_hit_rate"],
        "retrieval_hit_rate_at_5": summary_at_5["retrieval_hit_rate"],
        "citation_coverage": summary_at_5["citation_coverage"],
        "average_total_latency_ms": summary_at_5["average_total_latency_ms"],
        "average_faithfulness": summary_at_5["average_faithfulness"],
        "average_context_relevance": summary_at_5["average_context_relevance"],
        "average_hallucination_risk": summary_at_5["average_hallucination_risk"],
        "top_k_3_run_id": summary_at_3["run_id"],
        "top_k_5_run_id": summary_at_5["run_id"],
        "top_k_3_report_url": f"/api/evaluations/runs/{summary_at_3['run_id']}/report.md",
        "top_k_5_report_url": f"/api/evaluations/runs/{summary_at_5['run_id']}/report.md",
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

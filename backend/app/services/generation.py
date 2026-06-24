"""Grounded prompt construction and answer generation providers."""

import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from openai import OpenAI

from ..config import get_settings


def build_prompt(question: str, results: list[dict]) -> str:
    """Build a constrained prompt from the retrieved source chunks."""
    context = "\n\n".join(
        f"[Source {index}: {item['document'].filename}, chunk {item['chunk'].chunk_index}]\n"
        f"{item['chunk'].content}"
        for index, item in enumerate(results, start=1)
    )

    return f"""Answer the question using only the context below. If the context is insufficient, say so plainly. Cite sources inline as [Source N].

Context:
{context}

Question: {question}
Answer:"""


def generate_answer(prompt: str) -> tuple[str, str]:
    """Generate a grounded answer using the active local or OpenAI provider."""
    settings = get_settings()

    if settings.use_openai:
        return _generate_with_openai(prompt)

    if not settings.local_llm_mode:
        raise RuntimeError("Enable LOCAL_LLM_MODE=true or USE_OPENAI=true")

    return _generate_with_ollama(prompt, settings.ollama_base_url, settings.ollama_model)


def _generate_with_openai(prompt: str) -> tuple[str, str]:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("USE_OPENAI=true requires OPENAI_API_KEY")

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {"role": "system", "content": "You are a precise retrieval-grounded assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    answer = response.choices[0].message.content or "No answer generated."
    return answer, settings.openai_chat_model


def _generate_with_ollama(prompt: str, base_url: str, model: str) -> tuple[str, str]:
    body = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0},
        }
    ).encode()
    request = Request(
        f"{base_url.rstrip('/')}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode())
    except URLError as exc:
        raise RuntimeError(
            "Ollama is not running or is unreachable. Start it with `ollama serve`, then pull a model with "
            f"`ollama pull {model}`. Expected Ollama at {base_url}."
        ) from exc
    except TimeoutError as exc:
        raise RuntimeError(
            "Ollama timed out. Confirm the local model has been pulled and has enough system resources."
        ) from exc

    if "error" in payload:
        raise RuntimeError(
            f"Ollama error: {payload['error']}. Run `ollama pull {model}` if the model is missing."
        )

    return payload.get("response", "No answer generated."), f"ollama/{model}"

"""Document chunking utilities."""


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text near word or paragraph boundaries while retaining overlap."""
    normalized_text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if not normalized_text:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(normalized_text):
        end = min(start + chunk_size, len(normalized_text))

        if end < len(normalized_text):
            paragraph_boundary = normalized_text.rfind("\n", start, end)
            word_boundary = normalized_text.rfind(" ", start, end)
            boundary = max(paragraph_boundary, word_boundary)
            if boundary > start + chunk_size // 2:
                end = boundary

        chunk = normalized_text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(normalized_text):
            break

        start = max(end - overlap, start + 1)

    return chunks

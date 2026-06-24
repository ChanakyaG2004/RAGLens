"""Text extraction for the document types supported by RAGLens."""

from io import BytesIO

class DocumentExtractionError(ValueError):
    """Raised when an uploaded document cannot provide usable text."""


def extract_text(filename: str, raw_content: bytes) -> str:
    """Extract text from UTF-8 text/Markdown or text-based PDF files."""
    extension = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if extension in {"txt", "md"}:
        try:
            return raw_content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise DocumentExtractionError("Text and Markdown files must be UTF-8 encoded") from exc

    if extension == "pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise DocumentExtractionError(
                "PDF support requires pypdf. Run: pip install -r requirements.txt"
            ) from exc
        try:
            reader = PdfReader(BytesIO(raw_content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            raise DocumentExtractionError("RAGLens could not read this PDF. Upload a valid, non-encrypted PDF.") from exc
        if not text.strip():
            raise DocumentExtractionError(
                "This PDF has no extractable text. Scanned/image-only PDFs need OCR before they can be indexed."
            )
        return text

    raise DocumentExtractionError("Only .txt, .md, and text-based .pdf files are supported")

from pathlib import Path


def route_document(path: Path, mime_type: str | None = None) -> str:
    """Choose a parser without mutating the raw document."""
    normalized_mime = (mime_type or "").lower().split(";", 1)[0].strip()
    if normalized_mime == "application/pdf" or path.suffix.lower() == ".pdf":
        return "pdf"
    if normalized_mime in {"text/html", "application/xhtml+xml"} or path.suffix.lower() in {".html", ".htm"}:
        return "html"
    return "unknown"

from pathlib import Path


def route_document(path: Path) -> str:
    """Choose a parser without mutating the raw document."""
    return "pdf" if path.suffix.lower() == ".pdf" else "html"

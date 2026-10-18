from __future__ import annotations

from pathlib import Path

from backend.app.scraper.models import PdfExtractionResult


def inspect_pdf(path: str | Path, extraction: PdfExtractionResult) -> dict:
    """Return factual, low-assumption properties for the Phase 1 audit."""
    value = extraction.full_text.casefold()
    expected_headers = ("batch", "manufactur", "expiry", "reported by", "laboratory")
    return {
        "file_size_bytes": Path(path).stat().st_size,
        "page_count": extraction.page_count,
        "machine_readable": extraction.extraction_success,
        "table_header_terms_detected": [term for term in expected_headers if term in value],
        "pages_without_text": [
            page.page_number for page in extraction.page_texts if not page.text.strip()
        ],
        "warnings": list(extraction.warnings),
    }

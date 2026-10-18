from pathlib import Path

import pymupdf

from backend.app.scraper.models import PdfExtractionResult, PdfPageText


class PdfExtractionError(RuntimeError):
    """Raised when a PDF cannot be opened or traversed."""


def extract_pdf_text(path: str | Path) -> PdfExtractionResult:
    """Extract page-separated text with PyMuPDF while retaining reading order as observed."""
    pdf_path = Path(path)
    try:
        document = pymupdf.open(pdf_path)
    except Exception as exc:  # PyMuPDF exposes several parser-specific exception types.
        raise PdfExtractionError(f"Unable to open PDF {pdf_path}: {exc}") from exc

    page_texts: list[PdfPageText] = []
    warnings: list[str] = []
    try:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text", sort=True)
            if not text.strip():
                warnings.append(f"Page {page_number} contains no extractable text")
            page_texts.append(PdfPageText(page_number=page_number, text=text))
    except Exception as exc:
        raise PdfExtractionError(f"Unable to extract PDF {pdf_path}: {exc}") from exc
    finally:
        document.close()

    full_text = "\n\n\f\n\n".join(page.text for page in page_texts)
    has_text = any(page.text.strip() for page in page_texts)
    if not has_text:
        warnings.append("Document contains no machine-readable text; OCR was not attempted")

    return PdfExtractionResult(
        page_count=len(page_texts),
        page_texts=page_texts,
        full_text=full_text,
        extraction_success=has_text,
        extraction_method="pymupdf",
        warnings=warnings,
    )

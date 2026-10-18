from __future__ import annotations

import time
from pathlib import Path

from backend.app.extraction.pdf_tables import extract_pdf_tables
from backend.app.extraction.pdf_text import extract_pdf_text
from backend.app.extraction.pdf_words import extract_pymupdf_words
from backend.app.extraction.pdfplumber_benchmark import extract_pdfplumber_words


def _measure(function, *args):
    started = time.perf_counter()
    result = function(*args)
    return result, round((time.perf_counter() - started) * 1000, 3)


def benchmark_document(path: str | Path, alert_type: str) -> dict:
    pdf_path = Path(path)
    plain, plain_ms = _measure(extract_pdf_text, pdf_path)
    pymupdf_words, pymupdf_ms = _measure(extract_pymupdf_words, pdf_path)
    plumber_words, plumber_words_ms = _measure(extract_pdfplumber_words, pdf_path)
    plumber_tables, plumber_tables_ms = _measure(extract_pdf_tables, pdf_path)

    tables = [table for page in plumber_tables for table in page["tables"]]
    table_rows = sum(len(table["rows"]) for table in tables)
    return {
        "document": pdf_path.name,
        "alert_type": alert_type,
        "page_count": plain.page_count,
        "methods": {
            "pymupdf_text": {
                "duration_ms": plain_ms,
                "characters": len(plain.full_text),
                "pages_with_text": sum(bool(page.text.strip()) for page in plain.page_texts),
            },
            "pymupdf_coordinates": {
                "duration_ms": pymupdf_ms,
                "word_count": sum(len(page["words"]) for page in pymupdf_words),
            },
            "pdfplumber_words": {
                "duration_ms": plumber_words_ms,
                "word_count": sum(len(page["words"]) for page in plumber_words),
            },
            "pdfplumber_tables": {
                "duration_ms": plumber_tables_ms,
                "table_count": len(tables),
                "extracted_row_count_including_headers_and_continuations": table_rows,
            },
        },
    }

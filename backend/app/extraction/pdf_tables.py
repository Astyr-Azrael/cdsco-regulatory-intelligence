from __future__ import annotations

from pathlib import Path

import pdfplumber


def extract_pdf_tables(path: str | Path) -> list[dict]:
    """Extract page-scoped pdfplumber tables without interpreting their meaning."""
    pages: list[dict] = []
    with pdfplumber.open(path) as document:
        for page_number, page in enumerate(document.pages, start=1):
            tables = page.find_tables()
            pages.append(
                {
                    "page_number": page_number,
                    "width": float(page.width),
                    "height": float(page.height),
                    "tables": [
                        {
                            "bbox": [float(value) for value in table.bbox],
                            "rows": table.extract(),
                        }
                        for table in tables
                    ],
                }
            )
    return pages

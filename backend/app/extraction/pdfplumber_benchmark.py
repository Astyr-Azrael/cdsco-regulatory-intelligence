from __future__ import annotations

from pathlib import Path

import pdfplumber


def extract_pdfplumber_words(path: str | Path) -> list[dict]:
    """Return pdfplumber words using its top-origin coordinate convention."""
    pages: list[dict] = []
    with pdfplumber.open(path) as document:
        for page_number, page in enumerate(document.pages, start=1):
            words = []
            for order, word in enumerate(page.extract_words()):
                words.append(
                    {
                        "text": word["text"],
                        "x0": float(word["x0"]),
                        "y0": float(word["top"]),
                        "x1": float(word["x1"]),
                        "y1": float(word["bottom"]),
                        "page_number": page_number,
                        "original_order": order,
                    }
                )
            pages.append(
                {
                    "page_number": page_number,
                    "width": float(page.width),
                    "height": float(page.height),
                    "words": words,
                }
            )
    return pages

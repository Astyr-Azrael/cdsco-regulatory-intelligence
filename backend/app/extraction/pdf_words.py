from __future__ import annotations

from pathlib import Path

import pymupdf


def extract_pymupdf_words(path: str | Path) -> list[dict]:
    """Return original PyMuPDF word order with page-level coordinates."""
    document = pymupdf.open(path)
    pages: list[dict] = []
    try:
        for page_number, page in enumerate(document, start=1):
            words = []
            for order, word in enumerate(page.get_text("words", sort=False)):
                x0, y0, x1, y1, text, block_no, line_no, word_no = word
                words.append(
                    {
                        "text": text,
                        "x0": float(x0),
                        "y0": float(y0),
                        "x1": float(x1),
                        "y1": float(y1),
                        "page_number": page_number,
                        "block_number": int(block_no),
                        "line_number": int(line_no),
                        "word_number": int(word_no),
                        "original_order": order,
                    }
                )
            pages.append(
                {
                    "page_number": page_number,
                    "width": float(page.rect.width),
                    "height": float(page.rect.height),
                    "words": words,
                }
            )
    finally:
        document.close()
    return pages

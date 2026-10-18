from pathlib import Path

import pymupdf
import pytest

from backend.app.extraction.pdf_text import PdfExtractionError, extract_pdf_text


def _write_pdf(path: Path, page_texts: list[str]) -> None:
    document = pymupdf.open()
    for value in page_texts:
        page = document.new_page()
        if value:
            page.insert_text((72, 72), value)
    document.save(path)
    document.close()


def test_extracts_multiple_pages_and_preserves_boundaries(tmp_path):
    path = tmp_path / "multi.pdf"
    _write_pdf(path, ["First page", "Second page"])

    result = extract_pdf_text(path)

    assert result.page_count == 2
    assert [page.page_number for page in result.page_texts] == [1, 2]
    assert "First page" in result.page_texts[0].text
    assert "Second page" in result.page_texts[1].text
    assert "\f" in result.full_text
    assert result.extraction_success is True


def test_empty_pdf_is_reported_without_ocr(tmp_path):
    path = tmp_path / "empty.pdf"
    _write_pdf(path, [""])

    result = extract_pdf_text(path)

    assert result.extraction_success is False
    assert any("OCR was not attempted" in warning for warning in result.warnings)


def test_unreadable_pdf_raises_clear_error(tmp_path):
    path = tmp_path / "broken.pdf"
    path.write_bytes(b"not a pdf")
    with pytest.raises(PdfExtractionError):
        extract_pdf_text(path)

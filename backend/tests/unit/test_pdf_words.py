import pymupdf

from backend.app.extraction.pdf_words import extract_pymupdf_words


def test_word_coordinates_preserve_page_and_order(tmp_path):
    path = tmp_path / "words.pdf"
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Batch ABC123")
    document.save(path)
    document.close()

    pages = extract_pymupdf_words(path)

    assert pages[0]["page_number"] == 1
    assert [word["text"] for word in pages[0]["words"]] == ["Batch", "ABC123"]
    assert pages[0]["words"][0]["original_order"] == 0
    assert pages[0]["words"][0]["x0"] < pages[0]["words"][0]["x1"]

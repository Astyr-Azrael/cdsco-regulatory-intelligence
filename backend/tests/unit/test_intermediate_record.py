from pathlib import Path

from backend.app.preprocessing.record_standardization import build_intermediate_record, write_jsonl
from backend.app.scraper.models import (
    AlertMetadata,
    DownloadResult,
    PdfExtractionResult,
    PdfPageText,
)


def test_intermediate_record_retains_evidence_and_null_fields(tmp_path):
    raw_path = tmp_path / "raw.pdf"
    raw_path.write_bytes(b"%PDF fixture")
    alert = AlertMetadata(
        alert_title="Official fixture",
        alert_type=None,
        publication_date=None,
        document_url="https://example.test/document",
        source_url="https://example.test/index",
        retrieved_at="2026-10-01T09:00:00Z",
    )
    download = DownloadResult(
        source_url=alert.source_url,
        document_url=alert.document_url,
        resolved_document_url="https://example.test/document.pdf",
        retrieved_at="2026-10-01T09:01:00Z",
        original_filename="document.pdf",
        local_raw_path=str(raw_path),
        content_hash_sha256="a" * 64,
        http_status=200,
        mime_type="application/pdf",
        file_size_bytes=12,
    )
    extraction = PdfExtractionResult(
        page_count=1,
        page_texts=[PdfPageText(1, "Raw  text\n")],
        full_text="Raw  text\n",
        extraction_success=True,
    )

    record = build_intermediate_record(alert, download, extraction, project_root=tmp_path)

    assert record["source"]["source_url"] == alert.source_url
    assert record["source"]["document_url"] == alert.document_url
    assert record["source"]["retrieved_at"] == download.retrieved_at
    assert record["source"]["content_hash_sha256"] == "a" * 64
    assert record["document"]["local_raw_path"] == "raw.pdf"
    assert record["parsed_fields"]["drug_name"] is None
    assert record["parsed_fields"]["batch_number"] is None
    assert record["extraction"]["full_text"] == "Raw  text\n"
    assert record["extraction"]["normalized_text"] == "Raw text"

    output = write_jsonl([record], tmp_path / "records.jsonl")
    assert output.exists()
    assert output.read_text(encoding="utf-8").count("\n") == 1

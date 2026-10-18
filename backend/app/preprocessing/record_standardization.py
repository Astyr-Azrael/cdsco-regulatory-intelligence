from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from backend.app.preprocessing.text_cleaning import normalize_extracted_text
from backend.app.scraper.models import AlertMetadata, DownloadResult, PdfExtractionResult


PARSED_FIELD_NAMES = (
    "drug_name",
    "manufacturer",
    "batch_number",
    "manufacturing_date",
    "expiry_date",
    "failure_reason",
    "testing_laboratory",
    "sample_authority",
)


def build_intermediate_record(
    alert: AlertMetadata,
    download: DownloadResult,
    extraction: PdfExtractionResult,
    project_root: str | Path | None = None,
) -> dict:
    raw_path = Path(download.local_raw_path)
    if project_root is not None:
        try:
            local_raw_path = raw_path.resolve().relative_to(Path(project_root).resolve()).as_posix()
        except ValueError:
            local_raw_path = str(raw_path)
    else:
        local_raw_path = str(raw_path)

    return {
        "source": {
            "source_url": alert.source_url,
            "document_url": alert.document_url,
            "resolved_document_url": download.resolved_document_url,
            "retrieved_at": download.retrieved_at,
            "content_hash_sha256": download.content_hash_sha256,
            "http_status": download.http_status,
        },
        "alert": {
            "alert_title": alert.alert_title,
            "alert_type": alert.alert_type,
            "publication_date": alert.publication_date,
        },
        "document": {
            "original_filename": download.original_filename,
            "local_raw_path": local_raw_path,
            "mime_type": download.mime_type,
            "file_size_bytes": download.file_size_bytes,
            "page_count": extraction.page_count,
            "extraction_method": extraction.extraction_method,
        },
        "extraction": {
            "extraction_success": extraction.extraction_success,
            "full_text": extraction.full_text,
            "normalized_text": normalize_extracted_text(extraction.full_text),
            "page_texts": [
                {
                    "page_number": page.page_number,
                    "text": page.text,
                    "normalized_text": normalize_extracted_text(page.text),
                }
                for page in extraction.page_texts
            ],
            "warnings": list(extraction.warnings),
        },
        "parsed_fields": {name: None for name in PARSED_FIELD_NAMES},
    }


def write_jsonl(records: list[dict], output_path: str | Path) -> Path:
    """Atomically replace the derived manifest so reruns never append duplicates."""
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False, dir=target.parent, suffix=".tmp"
        ) as temporary:
            temporary_path = Path(temporary.name)
            for record in records:
                temporary.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        os.replace(temporary_path, target)
        temporary_path = None
        return target
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

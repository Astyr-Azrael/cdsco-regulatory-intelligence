"""Idempotently load Phase 1 source metadata and Phase 2 parsed rows."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database.models import IngestionRun, ParsedRegulatoryRecord, SourceDocument
from backend.app.database.session import SessionLocal, create_database


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def load() -> dict:
    source_path = PROJECT_ROOT / "data" / "interim" / "cdsco_alert_records.jsonl"
    parsed_path = PROJECT_ROOT / "data" / "interim" / "parsed_regulatory_records.jsonl"
    if not source_path.exists() or not parsed_path.exists():
        raise FileNotFoundError("Run scripts/process_documents.py and scripts/extract_regulatory_rows.py first")

    create_database()
    source_metadata = {item["source"]["content_hash_sha256"]: item for item in read_jsonl(source_path)}
    rows = read_jsonl(parsed_path)
    with SessionLocal() as db:
        run = IngestionRun(source_system="CDSCO_LEGACY_PDF", status="RUNNING", parser_version=rows[0]["parser_version"] if rows else None, records_seen=len(rows))
        db.add(run)
        db.flush()
        inserted = updated = 0
        sources: dict[str, SourceDocument] = {}

        for row in rows:
            digest = row["source_document_id"].removeprefix("sha256:")
            source = sources.get(digest) or db.scalar(select(SourceDocument).where(SourceDocument.content_hash_sha256 == digest))
            if source is None:
                metadata = source_metadata.get(digest, {})
                source_info = metadata.get("source", {})
                alert = metadata.get("alert", {})
                document = metadata.get("document", {})
                source = SourceDocument(
                    source_system="CDSCO_LEGACY_PDF",
                    source_url=source_info.get("source_url"),
                    document_url=source_info.get("resolved_document_url") or source_info.get("document_url"),
                    alert_title=alert.get("alert_title") or Path(row["source_filename"]).stem,
                    alert_type=row["alert_type"],
                    publication_date=alert.get("publication_date"),
                    retrieved_at=source_info.get("retrieved_at"),
                    original_filename=document.get("original_filename") or row["source_filename"],
                    local_raw_path=document.get("local_raw_path"),
                    content_hash_sha256=digest,
                    mime_type=document.get("mime_type", "application/pdf"),
                    page_count=document.get("page_count"),
                    extraction_status="ROW_EXTRACTED",
                )
                db.add(source)
                db.flush()
            sources[digest] = source

            record = db.scalar(select(ParsedRegulatoryRecord).where(ParsedRegulatoryRecord.source_document_id == source.id, ParsedRegulatoryRecord.source_row == row["source_row"]))
            values = {
                "source_page": row["source_page"], "source_bbox": row.get("source_bbox"), "alert_type": row["alert_type"],
                "raw_drug_name": row.get("drug_name"), "raw_batch_number": row.get("batch_number"), "raw_manufacturer": row.get("manufacturer"),
                "raw_manufacturer_address": row.get("manufacturer_address"), "raw_manufacturing_date": row.get("manufacturing_date"), "raw_expiry_date": row.get("expiry_date"),
                "raw_failure_reason": row.get("failure_reason"), "raw_laboratory": row.get("testing_laboratory"), "raw_authority": row.get("sample_authority"),
                "raw_remarks": row.get("remarks"), "raw_firm_reply": row.get("firm_reply"), "raw_cells": row.get("raw_cells"), "raw_row_text": row["raw_row_text"],
                "parsed_manufacturing_date": row.get("parsed_manufacturing_date"), "parsed_expiry_date": row.get("parsed_expiry_date"),
                "parse_status": row["parse_status"], "parser_name": row["parser_name"], "parser_version": row["parser_version"], "warnings": row.get("warnings", []),
            }
            if record is None:
                db.add(ParsedRegulatoryRecord(source_document_id=source.id, source_row=row["source_row"], **values))
                inserted += 1
            else:
                for key, value in values.items():
                    setattr(record, key, value)
                updated += 1

        run.status = "COMPLETED"
        run.completed_at = datetime.now(timezone.utc)
        run.records_inserted = inserted
        run.records_updated = updated
        db.commit()
        return {"run_id": run.id, "source_documents": len(sources), "records_seen": len(rows), "inserted": inserted, "updated": updated}


if __name__ == "__main__":
    print(json.dumps(load(), indent=2))

"""Fetch one public CDSCO current-NSQ snapshot and persist it with provenance."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database.models import IngestionRun, ParsedRegulatoryRecord, SourceDocument
from backend.app.database.session import SessionLocal, create_database
from backend.app.scraper.sources.cdsco_current_nsq import DATA_URL, PAGE_URL, fetch_current_nsq, save_raw_response, standardize_row


def main() -> int:
    content, payload = fetch_current_nsq(user_agent=os.getenv("SCRAPER_USER_AGENT", "cdsco-regulatory-intelligence-research/0.3 (+academic prototype)"))
    raw_path, digest = save_raw_response(content, PROJECT_ROOT / "data" / "raw" / "json")
    rows = payload["aaData"]
    reporting_months = sorted({row.get("dt_reporting_month_year") for row in rows if row.get("dt_reporting_month_year")})
    publication_label = ", ".join(reporting_months) or "current"
    publication_date = None
    if len(reporting_months) == 1:
        try:
            publication_date = datetime.strptime(reporting_months[0].title(), "%b-%Y").strftime("%Y-%m-01")
        except ValueError:
            pass
    create_database()
    with SessionLocal() as db:
        existing = db.scalar(select(SourceDocument).where(SourceDocument.content_hash_sha256 == digest))
        if existing:
            print(json.dumps({"status": "unchanged", "source_document_id": existing.id, "records": len(existing.records), "sha256": digest}, indent=2))
            return 0
        run = IngestionRun(source_system="CDSCO_CURRENT_NSQ_PORTAL", status="RUNNING", parser_version="phase2-0.1.0", records_seen=len(rows))
        db.add(run)
        source = SourceDocument(source_system="CDSCO_CURRENT_NSQ_PORTAL", source_url=PAGE_URL, document_url=PAGE_URL, alert_title=f"CDSCO Public NSQ Portal — {publication_label}", alert_type="NSQ", publication_date=publication_date, retrieved_at=datetime.now(timezone.utc).isoformat(), original_filename=raw_path.name, local_raw_path=str(raw_path.relative_to(PROJECT_ROOT)), content_hash_sha256=digest, mime_type="application/json", page_count=None, extraction_status="STRUCTURED_SOURCE_INGESTED")
        db.add(source)
        db.flush()
        for position, item in enumerate(rows, start=1):
            db.add(ParsedRegulatoryRecord(source_document_id=source.id, **standardize_row(item, position)))
        run.status = "COMPLETED"
        run.completed_at = datetime.now(timezone.utc)
        run.records_inserted = len(rows)
        db.commit()
        print(json.dumps({"status": "ingested", "source_document_id": source.id, "records": len(rows), "reporting_months": reporting_months, "sha256": digest}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

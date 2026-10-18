"""Restore the frozen official portal JSON into a fresh database without network."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from datetime import datetime,timezone
from pathlib import Path
from sqlalchemy import select

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.app.database.models import SourceDocument,ParsedRegulatoryRecord,IngestionRun
from backend.app.database.session import create_database,SessionLocal
from backend.app.scraper.sources.cdsco_current_nsq import validate_payload,standardize_row,PAGE_URL


def restore():
    manifest=json.loads((ROOT/"docs/release-verification.json").read_text(encoding="utf-8"))
    item=next(s for s in manifest["corpus"] if s["source_system"]=="CDSCO_CURRENT_NSQ_PORTAL")
    path=ROOT/item["local_raw_path"].replace("\\","/")
    content=path.read_bytes()
    digest=hashlib.sha256(content).hexdigest()
    if digest!=item["sha256"]: raise ValueError("Snapshot hash differs from frozen evidence")
    payload=json.loads(content)
    validate_payload(payload)
    create_database()
    with SessionLocal() as db:
        source=db.scalar(select(SourceDocument).where(SourceDocument.content_hash_sha256==digest))
        if source: return {"status":"unchanged","records":len(source.records)}
        source=SourceDocument(source_system="CDSCO_CURRENT_NSQ_PORTAL",source_url=PAGE_URL,document_url=PAGE_URL,
            alert_title=item["title"],alert_type="NSQ",publication_date=item["date"],
            original_filename=path.name,local_raw_path=path.relative_to(ROOT).as_posix(),content_hash_sha256=digest,
            retrieved_at="2026-10-02T07:13:38Z",mime_type="application/json",extraction_status="STRUCTURED_SOURCE_INGESTED")
        db.add(source);db.flush()
        for position,row in enumerate(payload["aaData"],1):
            db.add(ParsedRegulatoryRecord(source_document_id=source.id,**standardize_row(row,position)))
        db.add(IngestionRun(source_system="FROZEN_PORTAL_RESTORE",status="COMPLETED",completed_at=datetime.now(timezone.utc),records_seen=len(payload["aaData"]),records_inserted=len(payload["aaData"]),parser_version="phase2-0.1.0"))
        db.commit()
    return {"status":"restored","records":len(payload["aaData"])}


if __name__=="__main__": print(json.dumps(restore(),indent=2))

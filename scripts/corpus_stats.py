"""Print final corpus, provenance and entity-resolution statistics."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from sqlalchemy import func, select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database.models import CanonicalDrug, CanonicalManufacturer, DrugAlias, EntityMatch, IngestionRun, ManufacturerAlias, ParsedRegulatoryRecord, SourceDocument
from backend.app.database.session import SessionLocal


def main() -> int:
    with SessionLocal() as db:
        grouped = lambda column: dict(db.execute(select(column, func.count()).group_by(column)).all())
        stats = {
            "records": db.scalar(select(func.count(ParsedRegulatoryRecord.id))) or 0,
            "sources": db.scalar(select(func.count(SourceDocument.id))) or 0,
            "ingestion_runs": db.scalar(select(func.count(IngestionRun.id))) or 0,
            "parse_statuses": grouped(ParsedRegulatoryRecord.parse_status),
            "event_types": grouped(ParsedRegulatoryRecord.alert_type),
            "canonical_manufacturers": db.scalar(select(func.count(CanonicalManufacturer.id))) or 0,
            "canonical_drugs": db.scalar(select(func.count(CanonicalDrug.id))) or 0,
            "manufacturer_aliases": db.scalar(select(func.count(ManufacturerAlias.id))) or 0,
            "drug_aliases": db.scalar(select(func.count(DrugAlias.id))) or 0,
            "fuzzy_review_candidates": db.scalar(select(func.count(EntityMatch.id)).where(EntityMatch.decision == "REVIEW")) or 0,
        }
    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__": raise SystemExit(main())

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from backend.app.database.models import CanonicalDrug, CanonicalManufacturer, DrugAlias, IngestionRun, ManufacturerAlias, ParsedRegulatoryRecord, SourceDocument
from backend.app.database.session import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def summary(db: Annotated[Session, Depends(get_db)]) -> dict:
    record_count = db.scalar(select(func.count(ParsedRegulatoryRecord.id))) or 0
    document_count = db.scalar(select(func.count(SourceDocument.id))) or 0
    product_count = db.scalar(select(func.count(distinct(ParsedRegulatoryRecord.raw_drug_name)))) or 0
    manufacturer_count = db.scalar(select(func.count(distinct(ParsedRegulatoryRecord.raw_manufacturer)))) or 0
    status_counts = dict(db.execute(select(ParsedRegulatoryRecord.parse_status, func.count()).group_by(ParsedRegulatoryRecord.parse_status)).all())
    type_counts = dict(db.execute(select(ParsedRegulatoryRecord.alert_type, func.count()).group_by(ParsedRegulatoryRecord.alert_type)).all())
    timeline = [{"publication_date": date, "count": count} for date, count in db.execute(select(SourceDocument.publication_date, func.count(ParsedRegulatoryRecord.id)).join(ParsedRegulatoryRecord).group_by(SourceDocument.publication_date).order_by(SourceDocument.publication_date)).all()]
    first_date, last_date = db.execute(select(func.min(SourceDocument.publication_date), func.max(SourceDocument.publication_date))).one()
    latest_run = db.scalar(select(IngestionRun).where(IngestionRun.status == "COMPLETED").order_by(IngestionRun.completed_at.desc()).limit(1))
    canonical_manufacturers = db.scalar(select(func.count(CanonicalManufacturer.id))) or 0
    canonical_drugs = db.scalar(select(func.count(CanonicalDrug.id))) or 0
    repeated_manufacturers = db.scalar(select(func.count()).select_from(select(ManufacturerAlias.entity_id).group_by(ManufacturerAlias.entity_id).having(func.count() > 1).subquery())) or 0
    repeated_drugs = db.scalar(select(func.count()).select_from(select(DrugAlias.entity_id).group_by(DrugAlias.entity_id).having(func.count() > 1).subquery())) or 0
    findings = db.execute(select(ParsedRegulatoryRecord.raw_failure_reason, func.count().label("count")).where(ParsedRegulatoryRecord.raw_failure_reason.is_not(None)).group_by(ParsedRegulatoryRecord.raw_failure_reason).order_by(func.count().desc()).limit(10)).all()
    return {
        "data_scope": "indexed_regulatory_corpus",
        "regulatory_records": record_count,
        "official_documents": document_count,
        "distinct_product_mentions": product_count,
        "distinct_manufacturer_mentions": manufacturer_count,
        "coverage": {"start": first_date, "end": last_date},
        "last_synchronized": latest_run.completed_at.isoformat() if latest_run and latest_run.completed_at else None,
        "parse_status": status_counts,
        "event_types": type_counts,
        "timeline": timeline,
        "entities": {"canonical_manufacturers": canonical_manufacturers, "canonical_drugs": canonical_drugs, "repeated_manufacturers": repeated_manufacturers, "repeated_drugs": repeated_drugs, "linked_manufacturer_mentions": db.scalar(select(func.count(ManufacturerAlias.id))) or 0, "linked_drug_mentions": db.scalar(select(func.count(DrugAlias.id))) or 0},
        "common_findings": [{"label": label, "count": count} for label, count in findings],
    }

from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from backend.app.database.models import DrugAlias, ManufacturerAlias, ParsedRegulatoryRecord, SourceDocument


def serialize_record(record: ParsedRegulatoryRecord) -> dict:
    source = record.source_document
    manufacturer_alias = record.manufacturer_alias
    drug_alias = record.drug_alias
    return {
        "id": record.id,
        "alert_type": record.alert_type,
        "drug_name": record.raw_drug_name,
        "batch_number": record.raw_batch_number,
        "manufacturer": record.raw_manufacturer,
        "manufacturer_address": record.raw_manufacturer_address,
        "manufacturing_date": record.raw_manufacturing_date,
        "expiry_date": record.raw_expiry_date,
        "parsed_manufacturing_date": record.parsed_manufacturing_date,
        "parsed_expiry_date": record.parsed_expiry_date,
        "regulatory_finding": record.raw_failure_reason,
        "testing_laboratory": record.raw_laboratory,
        "sample_authority": record.raw_authority,
        "remarks": record.raw_remarks,
        "firm_reply": record.raw_firm_reply,
        "parse_status": record.parse_status,
        "parser_version": record.parser_version,
        "warnings": record.warnings or [],
        "canonical_manufacturer": ({
            "id": manufacturer_alias.entity.id,
            "name": manufacturer_alias.entity.canonical_name,
            "source_mention": manufacturer_alias.source_mention,
            "match_method": manufacturer_alias.match_method,
            "match_score": manufacturer_alias.match_score,
            "review_status": manufacturer_alias.review_status,
        } if manufacturer_alias else None),
        "canonical_drug": ({
            "id": drug_alias.entity.id,
            "name": drug_alias.entity.canonical_name,
            "source_mention": drug_alias.source_mention,
            "match_method": drug_alias.match_method,
            "match_score": drug_alias.match_score,
            "review_status": drug_alias.review_status,
        } if drug_alias else None),
        "provenance": {
            "source_document_id": source.id,
            "source_system": source.source_system,
            "title": source.alert_title,
            "publication_date": source.publication_date,
            "date_precision": "month" if source.source_system == "CDSCO_CURRENT_NSQ_PORTAL" else "day",
            "date_semantics": "reporting month, represented by month start for sorting" if source.source_system == "CDSCO_CURRENT_NSQ_PORTAL" else "publication date",
            "document_url": source.document_url,
            "source_url": source.source_url,
            "content_hash_sha256": source.content_hash_sha256,
            "page": record.source_page,
            "row": record.source_row,
            "bbox": record.source_bbox,
            "raw_row_text": record.raw_row_text,
        },
    }


def list_records(db: Session, *, query: str | None = None, alert_type: str | None = None, source_id: int | None = None, authority: str | None = None, year: int | None = None, page: int = 1, page_size: int = 25) -> dict:
    statement = select(ParsedRegulatoryRecord).join(ParsedRegulatoryRecord.source_document).options(joinedload(ParsedRegulatoryRecord.source_document), joinedload(ParsedRegulatoryRecord.manufacturer_alias).joinedload(ManufacturerAlias.entity), joinedload(ParsedRegulatoryRecord.drug_alias).joinedload(DrugAlias.entity))
    count_statement = select(func.count(ParsedRegulatoryRecord.id)).join(ParsedRegulatoryRecord.source_document)
    conditions = []
    if query:
        pattern = f"%{query.strip()}%"
        conditions.append(or_(ParsedRegulatoryRecord.raw_drug_name.ilike(pattern), ParsedRegulatoryRecord.raw_batch_number.ilike(pattern), ParsedRegulatoryRecord.raw_manufacturer.ilike(pattern), ParsedRegulatoryRecord.raw_failure_reason.ilike(pattern), ParsedRegulatoryRecord.raw_laboratory.ilike(pattern), ParsedRegulatoryRecord.raw_authority.ilike(pattern), SourceDocument.alert_title.ilike(pattern)))
    if alert_type:
        conditions.append(ParsedRegulatoryRecord.alert_type == alert_type)
    if source_id:
        conditions.append(ParsedRegulatoryRecord.source_document_id == source_id)
    if authority:
        pattern = f"%{authority.strip()}%"
        conditions.append(or_(ParsedRegulatoryRecord.raw_laboratory.ilike(pattern), ParsedRegulatoryRecord.raw_authority.ilike(pattern)))
    if year:
        conditions.append(SourceDocument.publication_date.like(f"{year}-%"))
    if conditions:
        statement = statement.where(*conditions)
        count_statement = count_statement.where(*conditions)
    total = db.scalar(count_statement) or 0
    records = db.scalars(statement.order_by(SourceDocument.publication_date.desc(), ParsedRegulatoryRecord.source_document_id, ParsedRegulatoryRecord.source_row).offset((page - 1) * page_size).limit(page_size)).unique().all()
    return {"items": [serialize_record(record) for record in records], "total": total, "page": page, "page_size": page_size}


def get_record(db: Session, record_id: int) -> dict | None:
    record = db.scalar(select(ParsedRegulatoryRecord).options(joinedload(ParsedRegulatoryRecord.source_document), joinedload(ParsedRegulatoryRecord.manufacturer_alias).joinedload(ManufacturerAlias.entity), joinedload(ParsedRegulatoryRecord.drug_alias).joinedload(DrugAlias.entity)).where(ParsedRegulatoryRecord.id == record_id))
    return serialize_record(record) if record else None

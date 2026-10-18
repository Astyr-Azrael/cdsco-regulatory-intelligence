from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.app.database.models import CanonicalDrug, CanonicalManufacturer, DrugAlias, EntityMatch, ManufacturerAlias
from backend.app.database.repository import get_record
from backend.app.database.session import get_db

router = APIRouter(prefix="/entities", tags=["entities"])


def _history(records):
    return sorted((r for r in records if r), key=lambda r: (
        r["provenance"].get("publication_date") is None,
        r["provenance"].get("publication_date") or "",
        r["provenance"]["source_document_id"], r["provenance"]["row"], r["id"],
    ))


def _evidence(aliases):
    return {"method": " / ".join(sorted({a.match_method for a in aliases})),
            "minimum_score": min((a.match_score for a in aliases), default=0),
            "score_meaning": "String similarity or normalized equality score; not identity confidence",
            "review_statuses": sorted({a.review_status for a in aliases})}


def _reviews(db, kind, aliases):
    keys={a.normalized_mention for a in aliases}
    rows=db.scalars(select(EntityMatch).where(EntityMatch.entity_type==kind,
        EntityMatch.review_status!="UNREVIEWED",
        or_(EntityMatch.left_normalized.in_(keys),EntityMatch.right_normalized.in_(keys)))).all()
    return [{"decision":r.decision,"score":r.match_score,"review_status":r.review_status,
             "reason":(r.evidence or {}).get("reason"),
             "reviewer":(r.evidence or {}).get("reviewer"),
             "source_evidence":(r.evidence or {}).get("source_evidence",[])} for r in rows]


def _manufacturer_payload(db: Session, entity: CanonicalManufacturer) -> dict:
    aliases = db.scalars(select(ManufacturerAlias).where(ManufacturerAlias.entity_id == entity.id).order_by(ManufacturerAlias.source_mention)).all()
    records = _history([get_record(db, alias.source_record_id) for alias in aliases])
    return {"id": entity.id, "entity_type": "MANUFACTURER", "identity_scope": "organization name; manufacturing sites remain source observations", "canonical_name": entity.canonical_name, "normalized_name": entity.normalized_name, "resolution_status": entity.resolution_status, "source_mentions": sorted({alias.source_mention for alias in aliases}), "addresses": sorted({alias.source_address for alias in aliases if alias.source_address}), "match_evidence": _evidence(aliases), "review_decisions": _reviews(db,"MANUFACTURER",aliases), "records": records, "record_count": len(records)}


def _drug_payload(db: Session, entity: CanonicalDrug) -> dict:
    aliases = db.scalars(select(DrugAlias).where(DrugAlias.entity_id == entity.id).order_by(DrugAlias.source_mention)).all()
    records = _history([get_record(db, alias.source_record_id) for alias in aliases])
    return {"id": entity.id, "entity_type": "DRUG", "canonical_name": entity.canonical_name, "normalized_name": entity.normalized_name, "strengths": entity.strengths or [], "dosage_forms": entity.dosage_forms or [], "resolution_status": entity.resolution_status, "source_mentions": sorted({alias.source_mention for alias in aliases}), "match_evidence": _evidence(aliases), "review_decisions": _reviews(db,"DRUG",aliases), "records": records, "record_count": len(records)}


@router.get("/search")
def search_entities(db: Annotated[Session, Depends(get_db)], q: str = Query(min_length=1)) -> dict:
    pattern = f"%{q.strip()}%"
    manufacturers = db.scalars(select(CanonicalManufacturer).outerjoin(ManufacturerAlias).where(or_(CanonicalManufacturer.canonical_name.ilike(pattern), ManufacturerAlias.source_mention.ilike(pattern))).distinct().limit(25)).all()
    drugs = db.scalars(select(CanonicalDrug).outerjoin(DrugAlias).where(or_(CanonicalDrug.canonical_name.ilike(pattern), DrugAlias.source_mention.ilike(pattern))).distinct().limit(25)).all()
    return {"manufacturers": [{"id": item.id, "name": item.canonical_name, "status": item.resolution_status, "record_count": db.scalar(select(func.count()).select_from(ManufacturerAlias).where(ManufacturerAlias.entity_id == item.id))} for item in manufacturers], "drugs": [{"id": item.id, "name": item.canonical_name, "status": item.resolution_status, "record_count": db.scalar(select(func.count()).select_from(DrugAlias).where(DrugAlias.entity_id == item.id))} for item in drugs]}


@router.get("/manufacturers/{entity_id}")
def get_manufacturer_entity(entity_id: int, db: Annotated[Session, Depends(get_db)]) -> dict:
    entity = db.get(CanonicalManufacturer, entity_id)
    if entity is None: raise HTTPException(404, "Canonical manufacturer not found")
    return _manufacturer_payload(db, entity)


@router.get("/drugs/{entity_id}")
def get_drug_entity(entity_id: int, db: Annotated[Session, Depends(get_db)]) -> dict:
    entity = db.get(CanonicalDrug, entity_id)
    if entity is None: raise HTTPException(404, "Canonical drug not found")
    return _drug_payload(db, entity)


@router.get("/review-queue")
def review_queue(db: Annotated[Session, Depends(get_db)], entity_type: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200)) -> dict:
    statement = select(EntityMatch).where(EntityMatch.decision == "REVIEW", EntityMatch.review_status == "UNREVIEWED")
    if entity_type: statement = statement.where(EntityMatch.entity_type == entity_type.upper())
    total = db.scalar(select(func.count()).select_from(statement.subquery()))
    rows = db.scalars(statement.order_by(EntityMatch.match_score.desc(), EntityMatch.id).offset((page-1)*page_size).limit(page_size)).all()
    return {"items": [{"id": row.id, "entity_type": row.entity_type, "left_mention": row.left_mention, "right_mention": row.right_mention, "score": row.match_score, "method": row.match_method, "decision": row.decision, "review_status": row.review_status, "evidence": row.evidence} for row in rows], "total": total, "page": page, "page_size": page_size}

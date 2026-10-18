from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.database.models import ParsedRegulatoryRecord, SourceDocument
from backend.app.database.session import get_db

router = APIRouter(prefix="/sources", tags=["sources"])


def serialize(source: SourceDocument, count: int) -> dict:
    return {"id": source.id, "source_system": source.source_system, "title": source.alert_title, "alert_type": source.alert_type, "publication_date": source.publication_date, "retrieved_at": source.retrieved_at, "filename": source.original_filename, "document_url": source.document_url, "source_url": source.source_url, "sha256": source.content_hash_sha256, "page_count": source.page_count, "extraction_status": source.extraction_status, "record_count": count}


@router.get("")
def list_sources(db: Annotated[Session, Depends(get_db)]) -> dict:
    rows = db.execute(select(SourceDocument, func.count(ParsedRegulatoryRecord.id)).outerjoin(ParsedRegulatoryRecord).group_by(SourceDocument.id).order_by(SourceDocument.publication_date.desc())).all()
    return {"items": [serialize(source, count) for source, count in rows], "total": len(rows)}


@router.get("/{source_id}")
def get_source(source_id: int, db: Annotated[Session, Depends(get_db)]) -> dict:
    row = db.execute(select(SourceDocument, func.count(ParsedRegulatoryRecord.id)).outerjoin(ParsedRegulatoryRecord).where(SourceDocument.id == source_id).group_by(SourceDocument.id)).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Source document not found")
    return serialize(row[0], row[1])

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from collections import defaultdict

from backend.app.database.repository import serialize_record
from backend.app.database.models import ParsedRegulatoryRecord, SourceDocument
from backend.app.database.session import get_db

router = APIRouter(prefix="/batches", tags=["batches"])


@router.get("/{batch_number}")
def get_batch(batch_number: str, db: Annotated[Session, Depends(get_db)]) -> dict:
    rows = db.scalars(select(ParsedRegulatoryRecord).join(ParsedRegulatoryRecord.source_document)
        .where(func.lower(func.trim(ParsedRegulatoryRecord.raw_batch_number)) == batch_number.strip().lower())
        .order_by(SourceDocument.publication_date, ParsedRegulatoryRecord.source_document_id, ParsedRegulatoryRecord.source_row)).all()
    items = [serialize_record(row) for row in rows]
    groups = defaultdict(list)
    for row, item in zip(rows, items):
        key = (row.drug_alias.entity_id if row.drug_alias else row.raw_drug_name,
               row.manufacturer_alias.entity_id if row.manufacturer_alias else row.raw_manufacturer,
               row.manufacturer_alias.normalized_address if row.manufacturer_alias else None)
        groups[key].append(item)
    return {"batch_number": batch_number, "items": items, "total": len(items),
            "identity_scope": "batch wording plus product and manufacturer site observation",
            "ambiguous": len(groups) > 1,
            "contexts": [{"product": values[0]["drug_name"], "manufacturer": values[0]["manufacturer"],
                          "items": values, "total": len(values)} for values in groups.values()]}

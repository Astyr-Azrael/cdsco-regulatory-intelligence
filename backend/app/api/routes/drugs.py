from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.repository import list_records
from backend.app.database.session import get_db

router = APIRouter(prefix="/drugs", tags=["drugs"])


@router.get("/{drug_name}")
def get_drug(drug_name: str, db: Annotated[Session, Depends(get_db)]) -> dict:
    matches = list_records(db, query=drug_name, page_size=100)
    exact = [item for item in matches["items"] if (item.get("drug_name") or "").casefold() == drug_name.casefold()]
    return {"source_mention": drug_name, "entity_status": "UNRESOLVED_SOURCE_MENTION", "items": exact, "total": len(exact)}

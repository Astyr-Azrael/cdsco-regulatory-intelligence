from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database.repository import list_records
from backend.app.database.session import get_db

router = APIRouter(tags=["search"])


@router.get("/search")
def search(
    db: Annotated[Session, Depends(get_db)],
    q: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    source: int | None = Query(default=None, ge=1),
    authority: str | None = Query(default=None),
    year: int | None = Query(default=None, ge=2010, le=2100),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
) -> dict:
    return list_records(db, query=q, alert_type=event_type, source_id=source, authority=authority, year=year, page=page, page_size=page_size)

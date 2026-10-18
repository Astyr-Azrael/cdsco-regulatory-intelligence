from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.repository import get_record
from backend.app.database.session import get_db

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/{event_id}")
def get_event(event_id: int, db: Annotated[Session, Depends(get_db)]) -> dict:
    record = get_record(db, event_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Regulatory record not found")
    return record

from __future__ import annotations

import hashlib
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.database.models import WebUsageEvent
from backend.app.database.session import get_db

router = APIRouter(prefix="/usage", tags=["usage analytics"])

ALLOWED_EVENTS = Literal["SEARCH_PERFORMED", "ENTITY_VIEWED", "RECORD_VIEWED", "FILTER_USED", "SOURCE_CLICKED", "ZERO_RESULT"]


class UsageEventInput(BaseModel):
    session_id: str = Field(min_length=8, max_length=200)
    event_type: ALLOWED_EVENTS
    entity_type: str | None = Field(default=None, max_length=24)
    entity_id: str | None = Field(default=None, max_length=120)
    query: str | None = Field(default=None, max_length=300)
    filters: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


@router.post("/events", status_code=202)
def record_usage(payload: UsageEventInput, db: Annotated[Session, Depends(get_db)]) -> dict:
    anonymous_session = hashlib.sha256(payload.session_id.encode("utf-8")).hexdigest()
    db.add(WebUsageEvent(session_id=anonymous_session, event_type=payload.event_type, entity_type=payload.entity_type, entity_id=payload.entity_id, query=payload.query, filters=payload.filters, metadata_json=payload.metadata))
    db.commit()
    return {"accepted": True}


@router.get("/summary")
def usage_summary(db: Annotated[Session, Depends(get_db)]) -> dict:
    counts = dict(db.execute(select(WebUsageEvent.event_type, func.count()).group_by(WebUsageEvent.event_type)).all())
    top_queries = db.execute(select(WebUsageEvent.query, func.count().label("count")).where(WebUsageEvent.query.is_not(None), WebUsageEvent.query != "").group_by(WebUsageEvent.query).order_by(func.count().desc()).limit(10)).all()
    top_entities = db.execute(select(WebUsageEvent.entity_type, WebUsageEvent.entity_id, func.count().label("count")).where(WebUsageEvent.event_type == "ENTITY_VIEWED").group_by(WebUsageEvent.entity_type, WebUsageEvent.entity_id).order_by(func.count().desc()).limit(10)).all()
    return {"scope": "anonymous_application_usage", "events": counts, "total_events": sum(counts.values()), "top_searches": [{"query": query, "count": count} for query, count in top_queries], "most_viewed_entities": [{"entity_type": kind, "entity_id": entity_id, "count": count} for kind, entity_id, count in top_entities]}

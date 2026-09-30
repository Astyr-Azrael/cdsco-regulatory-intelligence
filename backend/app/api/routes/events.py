from fastapi import APIRouter

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/{event_id}")
def get_event(event_id: str) -> dict:
    return {"id": event_id, "status": "repository scaffold"}

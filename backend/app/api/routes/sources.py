from fastapi import APIRouter

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("/{source_id}")
def get_source(source_id: str) -> dict:
    return {"id": source_id, "status": "repository scaffold"}

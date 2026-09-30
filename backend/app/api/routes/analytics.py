from fastapi import APIRouter

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def summary() -> dict:
    return {"data_scope": "verified-sample", "status": "repository scaffold"}

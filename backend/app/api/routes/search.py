from fastapi import APIRouter, Query

router = APIRouter(tags=["search"])


@router.get("/search")
def search(q: str = Query(min_length=1)) -> dict:
    return {"query": q, "results": [], "status": "sample repository not loaded"}

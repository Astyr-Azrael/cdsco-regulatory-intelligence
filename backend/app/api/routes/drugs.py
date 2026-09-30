from fastapi import APIRouter

router = APIRouter(prefix="/drugs", tags=["drugs"])


@router.get("/{drug_id}")
def get_drug(drug_id: str) -> dict:
    return {"id": drug_id, "status": "repository scaffold"}

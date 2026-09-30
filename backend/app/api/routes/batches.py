from fastapi import APIRouter

router = APIRouter(prefix="/batches", tags=["batches"])


@router.get("/{batch_number}")
def get_batch(batch_number: str) -> dict:
    return {"batch_number": batch_number, "status": "repository scaffold"}

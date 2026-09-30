from fastapi import APIRouter

router = APIRouter(prefix="/manufacturers", tags=["manufacturers"])


@router.get("/{manufacturer_id}")
def get_manufacturer(manufacturer_id: str) -> dict:
    return {"id": manufacturer_id, "status": "repository scaffold"}

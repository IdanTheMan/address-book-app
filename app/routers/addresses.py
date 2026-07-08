from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import AddressCreate, AddressResponse


router = APIRouter(prefix="/addresses", tags=["addresses"])

@router.post(
    "/",
    response_model=AddressResponse,
    status_code=201,
    summary="Create a new address",
)
def create_address(
    address: AddressCreate,
    db: Session = Depends(get_db),
) -> AddressResponse:
    try:
        return crud.create_address(db, address)
    except IntegrityError as exc:
        raise HTTPException(status_code=400, detail="Data integrity error") from exc

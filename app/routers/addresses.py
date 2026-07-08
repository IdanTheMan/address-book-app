"""Address book API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import AddressCreate, AddressResponse

logger = logging.getLogger(__name__)

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
    """Accept an address payload, validate it, and store it in the database."""
    logger.info("POST /addresses — creating: %s, %s", address.street, address.city)
    try:
        return crud.create_address(db, address)
    except IntegrityError as exc:
        logger.error("Integrity error creating address: %s", exc)
        raise HTTPException(status_code=400, detail="Data integrity error") from exc

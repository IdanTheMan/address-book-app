"""Address book API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import AddressCreate, AddressResponse, AddressUpdate

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


@router.get(
    "/",
    response_model=list[AddressResponse],
    summary="List all addresses (paginated)",
)
def list_addresses(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    db: Session = Depends(get_db),
) -> list[AddressResponse]:
    """Return a paginated list of all stored addresses."""
    logger.info("GET /addresses?skip=%d&limit=%d", skip, limit)
    return crud.get_addresses(db, skip=skip, limit=limit)


@router.get(
    "/{address_id}",
    response_model=AddressResponse,
    summary="Get a single address by ID",
)
def get_address(
    address_id: int,
    db: Session = Depends(get_db),
) -> AddressResponse:
    """Retrieve a single address by its ID."""
    logger.info("GET /addresses/%d", address_id)
    address = crud.get_address(db, address_id)
    if address is None:
        raise HTTPException(status_code=404, detail=f"Address {address_id} not found")
    return address


@router.put(
    "/{address_id}",
    response_model=AddressResponse,
    summary="Update an address (partial)",
)
def update_address(
    address_id: int,
    address: AddressUpdate,
    db: Session = Depends(get_db),
) -> AddressResponse:
    """Partially update an existing address."""
    logger.info("PUT /addresses/%d", address_id)
    try:
        updated = crud.update_address(db, address_id, address)
    except IntegrityError as exc:
        logger.error("Integrity error updating address %d: %s", address_id, exc)
        raise HTTPException(status_code=400, detail="Data integrity error") from exc
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Address {address_id} not found")
    return updated


@router.delete(
    "/{address_id}",
    status_code=204,
    summary="Delete an address",
)
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete an address by its ID."""
    logger.info("DELETE /addresses/%d", address_id)
    if not crud.delete_address(db, address_id):
        raise HTTPException(status_code=404, detail=f"Address {address_id} not found")
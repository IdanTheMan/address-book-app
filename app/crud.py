"""Database operations for addresses."""

import logging
from sqlalchemy.orm import Session

from app.models import Address
from app.schemas import AddressCreate, AddressUpdate

logger = logging.getLogger(__name__)

def create_address(db: Session, data: AddressCreate) -> Address:
    """Persist a new address and return it."""
    logger.info("Creating address: %s, %s", data.street, data.city)
    address = Address(**data.model_dump())
    db.add(address)
    db.commit()
    db.refresh(address)
    logger.info("Created address id=%d", address.id)
    return address

def get_addresses(db: Session, skip: int = 0, limit: int = 100) -> list[Address]:
    """Return a paginated list of all addresses."""
    logger.debug("Listing addresses (skip=%d, limit=%d)", skip, limit)
    return db.query(Address).offset(skip).limit(limit).all()


def get_addresses(db: Session, skip: int = 0, limit: int = 100) -> list[Address]:
    """Return a paginated list of all addresses."""
    logger.debug("Listing addresses (skip=%d, limit=%d)", skip, limit)
    return db.query(Address).offset(skip).limit(limit).all()


def update_address(
    db: Session, address_id: int, data: AddressUpdate
) -> Address | None:
    """Apply a partial update. Returns the updated address or None if not found."""
    logger.info("Updating address id=%d", address_id)
    address = get_address(db, address_id)
    if address is None:
        logger.warning("Address id=%d not found — update skipped", address_id)
        return None

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(address, field, value)

    db.commit()
    db.refresh(address)
    logger.info("Updated address id=%d", address_id)
    return address
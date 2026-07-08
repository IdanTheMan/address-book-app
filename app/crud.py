"""Database operations for addresses."""

import logging
from sqlalchemy.orm import Session

from app.models import Address
from app.schemas import AddressCreate

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

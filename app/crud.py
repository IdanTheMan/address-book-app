
from sqlalchemy.orm import Session

from app.models import Address
from app.schemas import AddressCreate


def create_address(db: Session, data: AddressCreate) -> Address:
    address = Address(**data.model_dump())
    db.add(address)
    db.commit()
    db.refresh(address)
    return address

"""Database operations for addresses."""

import logging
import math

from geopy.distance import geodesic
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


def get_address(db: Session, address_id: int) -> Address | None:
    """Return a single address by primary key, or None."""
    logger.debug("Fetching address id=%d", address_id)
    return db.query(Address).filter(Address.id == address_id).first()


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


def delete_address(db: Session, address_id: int) -> bool:
    """Delete an address. Returns True on success, False if not found."""
    logger.info("Deleting address id=%d", address_id)
    address = get_address(db, address_id)
    if address is None:
        logger.warning("Address id=%d not found — delete skipped", address_id)
        return False

    db.delete(address)
    db.commit()
    logger.info("Deleted address id=%d", address_id)
    return True


# Mean radius used to convert km <-> degrees for the bounding-box pre-filter
_KM_PER_DEG_LAT = 111.32
def get_nearby_addresses(
    db: Session,
    latitude: float,
    longitude: float,
    distance_km: float,
) -> list[tuple[Address, float]]:
    """
    Return addresses within *distance_km* of the given point.

    A bounding-box pre-filter narrows candidates via SQL before the exact
    geodesic distance is calculated in Python with ``geopy``.
    Results are sorted by distance (ascending).
    """
    logger.info(
        "Searching within %.1f km of (%.4f, %.4f)",
        distance_km, latitude, longitude,
    )

    # ---- bounding-box approximation (fast, SQL-only) --------------------
    lat_delta = distance_km / _KM_PER_DEG_LAT

    cos_lat = math.cos(math.radians(latitude))
    if abs(cos_lat) < 1e-10:
        # Near the poles — all longitudes converge, search everything
        min_lon, max_lon = -180.0, 180.0
    else:
        lon_delta = distance_km / (_KM_PER_DEG_LAT * cos_lat)
        min_lon = max(longitude - lon_delta, -180.0)
        max_lon = min(longitude + lon_delta, 180.0)

    min_lat = max(latitude - lat_delta, -90.0)
    max_lat = min(latitude + lat_delta, 90.0)

    candidates = (
        db.query(Address)
        .filter(
            Address.latitude.between(min_lat, max_lat),
            Address.longitude.between(min_lon, max_lon),
        )
        .all()
    )
    logger.debug("Bounding-box returned %d candidate(s)", len(candidates))

    # ---- exact geodesic refinement (WGS-84) -----------------------------
    origin = (latitude, longitude)
    results: list[tuple[Address, float]] = []
    for addr in candidates:
        km = geodesic(origin, (addr.latitude, addr.longitude)).kilometers
        if km <= distance_km:
            results.append((addr, km))

    results.sort(key=lambda pair: pair[1])
    logger.info("Found %d address(es) within radius", len(results))
    return results
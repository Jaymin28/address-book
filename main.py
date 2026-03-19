"""
Address Book API
================
A FastAPI application for managing addresses with geolocation support.
Supports full CRUD operations and proximity-based address search.
"""

import logging
import time
from fastapi import FastAPI, HTTPException, Depends, Query, Response
from sqlalchemy.orm import Session
from typing import List
import math

from database.session import get_db, engine
from models.address import Address
from models import schemas

# Basic app logging. Uvicorn will still manage its own access logs; this adds app-level events.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("addressbook")

# Create tables on startup
Address.metadata.create_all(bind=engine)

app = FastAPI(
    title="Address Book API",
    description="""
## Address Book with Geolocation Support

A RESTful API for managing addresses with coordinate-based proximity search.

### Features
- Full CRUD operations for addresses
- Coordinates (latitude & longitude) stored with each address
- Search addresses within a given distance from a point
- Input validation for all fields including coordinate ranges
- Persistent SQLite storage

### Distance Calculation
Uses the **Haversine formula** to compute great-circle distance between coordinates.
Distance is returned in **kilometers**.
    """,
    version="1.0.0",
    contact={
        "name": "Address Book API",
    },
)


@app.middleware("http")
async def log_requests(request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.exception(
            "request_failed method=%s path=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "request_handled method=%s path=%s status=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response

# ──────────────────────────────────────────────
#  Haversine distance formula
# ──────────────────────────────────────────────

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth (in km).
    Uses the Haversine formula.
    """
    R = 6371.0  # Earth's radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# ──────────────────────────────────────────────
#  Routes
# ──────────────────────────────────────────────

@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Address Book API is running. Visit /docs for Swagger UI."}


@app.post(
    "/address",
    response_model=schemas.AddressResponse,
    status_code=201,
    summary="Create a new address"
)
def create_address(address: schemas.AddressCreate, db: Session = Depends(get_db)):
    """
    Create a new address entry.

    - name: A label for the address (e.g. "Home", "Office")
    - street: Street name and number
    - city: City name
    - state: State or province
    - country: Country name
    - postal_code: ZIP / postal code
    - latitude: Decimal degrees, range -90 to 90
    - longitude: Decimal degrees, range -180 to 180
    """
    db_address = Address(**address.model_dump())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    logger.info("address_created id=%s name=%s city=%s", db_address.id, db_address.name, db_address.city)
    return db_address


@app.get(
    "/addresses",
    response_model=List[schemas.AddressResponse],
    summary="List all addresses"
)
def list_addresses(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Maximum records to return"),
    db: Session = Depends(get_db),
):
    """Retrieve a paginated list of all addresses."""
    return db.query(Address).offset(skip).limit(limit).all()


@app.get(
    "/addresses/nearby",
    response_model=List[schemas.AddressWithDistance],
    summary="Find addresses within a given distance"
)
def get_nearby_addresses(
    latitude: float = Query(..., ge=-90, le=90, description="Center point latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Center point longitude"),
    distance_km: float = Query(..., gt=0, description="Search radius in kilometers"),
    db: Session = Depends(get_db),
):
    """
    Retrieve all addresses within distance_km kilometers of the given coordinates.

    Results are sorted by distance (nearest first) and include the computed distance.

    - latitude: Center latitude (-90 to 90)
    - longitude: Center longitude (-180 to 180)
    - distance_km: Radius in kilometers (must be > 0)
    """
    all_addresses = db.query(Address).all()

    nearby = []
    for addr in all_addresses:
        dist = haversine_distance(latitude, longitude, addr.latitude, addr.longitude)
        if dist <= distance_km:
            nearby.append(schemas.AddressWithDistance(
                **{c.name: getattr(addr, c.name) for c in addr.__table__.columns},
                distance_km=round(dist, 3),
            ))

    nearby.sort(key=lambda x: x.distance_km)
    return nearby


@app.get(
    "/address/{address_id}",
    response_model=schemas.AddressResponse,
    summary="Get a single address by ID"
)
def get_address(address_id: int, db: Session = Depends(get_db)):
    """Fetch a specific address by its ID."""
    address = db.query(Address).filter(Address.id == address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail=f"Address with id={address_id} not found.")
    return address


@app.put(
    "/address/{address_id}",
    response_model=schemas.AddressResponse,
    summary="Update an existing address"
)
def update_address(address_id: int, updated: schemas.AddressUpdate, db: Session = Depends(get_db)):
    """
    Update one or more fields of an existing address.

    Only the provided fields will be updated (partial update supported).
    """
    address = db.query(Address).filter(Address.id == address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail=f"Address with id={address_id} not found.")

    update_data = updated.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(address, field, value)

    db.commit()
    db.refresh(address)
    logger.info("address_updated id=%s fields=%s", address.id, sorted(update_data.keys()))
    return address


@app.delete(
    "/address/{address_id}",
    status_code=204,
    summary="Delete an address"
)
def delete_address(address_id: int, db: Session = Depends(get_db)):
    """Permanently delete an address by its ID."""
    address = db.query(Address).filter(Address.id == address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail=f"Address with id={address_id} not found.")

    db.delete(address)
    db.commit()
    logger.info("address_deleted id=%s", address_id)
    # 204 responses must not include a body.
    return Response(status_code=204)

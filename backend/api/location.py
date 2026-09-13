"""
Location endpoints: read the user's last known location, and attach/save a
confirmed accident location.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.database_models import Accident, User
from models.schemas import LocationUpdate, AccidentLocation
from api.auth import get_current_user

router = APIRouter(prefix="/api", tags=["Location"])

# In-memory "last known location" per user - a lightweight development stand-in
# for a real live-location table. Resets on backend restart.
_last_location_by_user = {}


@router.get("/location")
def get_last_location(current_user: User = Depends(get_current_user)):
    loc = _last_location_by_user.get(current_user.id)
    if not loc:
        raise HTTPException(status_code=404, detail="No location reported yet for this user")
    return loc


@router.post("/location")
def update_location(payload: LocationUpdate, current_user: User = Depends(get_current_user)):
    _last_location_by_user[current_user.id] = payload.model_dump()
    return {"status": "ok", "location": payload}


@router.post("/accident/location")
def save_accident_location(
    payload: AccidentLocation,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    accident = db.query(Accident).filter(
        Accident.id == payload.accident_id, Accident.user_id == current_user.id
    ).first()
    if not accident:
        raise HTTPException(status_code=404, detail="Accident not found")

    accident.latitude = payload.latitude
    accident.longitude = payload.longitude
    db.commit()
    return {"status": "ok", "accident_id": accident.id}

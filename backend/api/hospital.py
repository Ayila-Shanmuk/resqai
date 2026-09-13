"""
Nearby hospital recommendation endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.database import get_db
from models.database_models import Accident, User
from models.schemas import Hospital
from services.hospital_service import get_nearby_hospitals
from api.auth import get_current_user

router = APIRouter(prefix="/api", tags=["Hospitals"])


@router.get("/hospitals/nearby", response_model=list[Hospital])
async def nearby_hospitals(
    latitude: float = Query(...),
    longitude: float = Query(...),
    accident_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        raise HTTPException(status_code=422, detail="Invalid latitude/longitude")

    try:
        hospitals = await get_nearby_hospitals(latitude, longitude)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Hospital lookup failed: {exc}")

    if accident_id and hospitals:
        accident = db.query(Accident).filter(
            Accident.id == accident_id, Accident.user_id == current_user.id
        ).first()
        if accident:
            accident.hospital = hospitals[0]["name"]
            db.commit()

    return hospitals

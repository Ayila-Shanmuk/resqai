"""
Accident detection + accident history endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.database_models import Accident, SensorData, User
from models.schemas import SensorInput, DetectionResponse, AccidentRecord
from services.accident_detection import detect_from_sensors
from api.auth import get_current_user

router = APIRouter(prefix="/api", tags=["Accident Detection"])

# Very small in-memory cache of each user's last known speed, used only to
# detect sudden deceleration between consecutive sensor readings. Resets on
# backend restart - acceptable for a development/demo project.
_last_speed_by_user = {}


@router.post("/detect-accident", response_model=DetectionResponse)
def detect_accident(
    payload: SensorInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        previous_speed = _last_speed_by_user.get(current_user.id)
        result = detect_from_sensors(payload.model_dump(), previous_speed=previous_speed)
        _last_speed_by_user[current_user.id] = payload.speed
    except (KeyError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=f"Invalid sensor payload: {exc}")

    accident_id = None
    # Only persist an Accident row when something is actually noteworthy,
    # to avoid flooding the history table with routine "normal" readings.
    if result["status"] in ("suspicious", "possible_accident"):
        accident = Accident(
            user_id=current_user.id,
            latitude=payload.latitude,
            longitude=payload.longitude,
            speed=payload.speed,
            detection_status=result["status"],
            status="pending",
            is_simulated=False,
        )
        db.add(accident)
        db.commit()
        db.refresh(accident)

        db.add(SensorData(
            accident_id=accident.id,
            accelerometer_x=payload.accelerometer_x,
            accelerometer_y=payload.accelerometer_y,
            accelerometer_z=payload.accelerometer_z,
            gyroscope_x=payload.gyroscope_x,
            gyroscope_y=payload.gyroscope_y,
            gyroscope_z=payload.gyroscope_z,
            speed=payload.speed,
        ))
        db.commit()
        accident_id = accident.id

    return DetectionResponse(
        status=result["status"],
        impact_magnitude=result["impact_magnitude"],
        rotation_magnitude=result["rotation_magnitude"],
        reason=result["reason"],
        accident_id=accident_id,
    )


@router.get("/accidents", response_model=List[AccidentRecord])
def list_accidents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    accidents = (
        db.query(Accident)
        .filter(Accident.user_id == current_user.id)
        .order_by(Accident.timestamp.desc())
        .all()
    )
    return accidents

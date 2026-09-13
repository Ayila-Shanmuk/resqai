"""
Emergency alert + confirmation-workflow endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.database_models import Accident, User
from models.schemas import EmergencyAlertRequest, EmergencyAlertResponse, ConfirmSafeRequest
from services.emergency_service import send_emergency_alert
from api.auth import get_current_user

router = APIRouter(prefix="/api", tags=["Emergency Response"])


@router.post("/emergency/alert", response_model=EmergencyAlertResponse)
def trigger_emergency_alert(
    payload: EmergencyAlertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    accident = db.query(Accident).filter(
        Accident.id == payload.accident_id, Accident.user_id == current_user.id
    ).first()
    if not accident:
        raise HTTPException(status_code=404, detail="Accident not found")

    result = send_emergency_alert(
        severity=payload.severity,
        latitude=payload.latitude if payload.latitude is not None else accident.latitude,
        longitude=payload.longitude if payload.longitude is not None else accident.longitude,
        accident_id=accident.id,
        message_override=payload.message_override,
    )

    accident.status = "confirmed"
    accident.emergency_alert_sent = True
    db.commit()

    return EmergencyAlertResponse(
        accident_id=accident.id,
        alert_sent=result["alert_sent"],
        simulated=result["simulated"],
        message=result["message"],
        sent_at=result["sent_at"],
        channel=result["channel"],
    )


@router.post("/emergency/confirm-safe")
def confirm_safe(
    payload: ConfirmSafeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    accident = db.query(Accident).filter(
        Accident.id == payload.accident_id, Accident.user_id == current_user.id
    ).first()
    if not accident:
        raise HTTPException(status_code=404, detail="Accident not found")

    accident.status = "false_alarm"
    accident.emergency_alert_sent = False
    db.commit()
    return {"status": "ok", "accident_id": accident.id, "message": "Marked as false alarm"}

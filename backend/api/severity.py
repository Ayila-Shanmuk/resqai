"""
Severity prediction + SHAP explanation endpoints.
"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.database_models import Accident, User
from models.schemas import (
    SeverityInput, SeverityResponse, ExplainRequest, ExplainResponse, FeatureContribution
)
from services.severity_prediction import predict_severity, explain_prediction, ModelNotTrainedError
from api.auth import get_current_user

router = APIRouter(prefix="/api", tags=["Severity Prediction"])


@router.post("/predict-severity", response_model=SeverityResponse)
def predict_severity_endpoint(
    payload: SeverityInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        severity, confidence, important_features = predict_severity(payload.model_dump())
    except ModelNotTrainedError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")

    if payload.accident_id:
        accident = db.query(Accident).filter(
            Accident.id == payload.accident_id, Accident.user_id == current_user.id
        ).first()
        if accident:
            accident.severity = severity
            accident.confidence = confidence
            db.commit()

    return SeverityResponse(
        severity=severity,
        confidence=round(confidence, 4),
        important_features=important_features,
        accident_id=payload.accident_id,
    )


@router.post("/explain-prediction", response_model=ExplainResponse)
def explain_prediction_endpoint(
    payload: ExplainRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        result = explain_prediction(payload.features.model_dump())
    except ModelNotTrainedError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {exc}")

    if payload.accident_id:
        accident = db.query(Accident).filter(
            Accident.id == payload.accident_id, Accident.user_id == current_user.id
        ).first()
        if accident:
            accident.explanation_json = json.dumps(result)
            db.commit()

    return ExplainResponse(
        predicted_severity=result["predicted_severity"],
        confidence=round(result["confidence"], 4),
        base_value=result["base_value"],
        contributions=[FeatureContribution(**c) for c in result["contributions"]],
        summary=result["summary"],
    )

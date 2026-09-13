"""
Inference-time utilities: load the trained model and produce severity
predictions plus SHAP-based explanations.
"""
import os
import json
from typing import Dict, List, Tuple
import numpy as np
import joblib

from ml.preprocessing import record_to_feature_row, FEATURE_COLUMNS

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
FEATURE_COLUMNS_PATH = os.path.join(os.path.dirname(__file__), "feature_columns.pkl")
LABEL_ENCODER_PATH = os.path.join(os.path.dirname(__file__), "label_encoder.pkl")
METRICS_PATH = os.path.join(os.path.dirname(__file__), "metrics.json")

_model = None
_feature_columns = None
_label_encoder = None
_explainer = None

# Human-readable labels for feature contribution output
FEATURE_DISPLAY_NAMES = {
    "speed": "Vehicle speed",
    "impact_magnitude": "Impact magnitude",
    "num_vehicles": "Number of vehicles involved",
    "num_occupants": "Number of occupants",
    "airbag_deployed": "Airbag deployment",
    "rollover": "Vehicle rollover",
}


def _friendly_feature_name(col: str) -> str:
    if col in FEATURE_DISPLAY_NAMES:
        return FEATURE_DISPLAY_NAMES[col]
    # e.g. "weather_Rain" -> "Weather: Rain"
    for prefix in ["weather", "road_condition", "vehicle_type", "lighting_condition", "road_type"]:
        if col.startswith(prefix + "_"):
            label = prefix.replace("_", " ").title()
            value = col[len(prefix) + 1:]
            return f"{label}: {value}"
    return col


class ModelNotTrainedError(Exception):
    """Raised when the model artifacts have not been trained/saved yet."""
    pass


def _ensure_loaded():
    global _model, _feature_columns, _label_encoder
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise ModelNotTrainedError(
                "No trained model found. Run `python ml/train_model.py` first."
            )
        _model = joblib.load(MODEL_PATH)
        _feature_columns = joblib.load(FEATURE_COLUMNS_PATH)
        _label_encoder = joblib.load(LABEL_ENCODER_PATH)


def get_training_metrics() -> Dict:
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH) as f:
            return json.load(f)
    return {}


def predict_severity(record: Dict) -> Tuple[str, float, List[str]]:
    """
    Returns (severity_label, confidence, top_3_important_feature_names)
    """
    _ensure_loaded()
    X = record_to_feature_row(record)[_feature_columns]

    proba = _model.predict_proba(X)[0]
    pred_idx = int(np.argmax(proba))
    severity = _label_encoder.inverse_transform([pred_idx])[0]
    confidence = float(proba[pred_idx])

    # Global feature importance as a fast stand-in for "important features"
    # on this endpoint (full per-prediction contribution lives in /explain).
    importances = getattr(_model, "feature_importances_", None)
    if importances is not None:
        top_idx = np.argsort(importances)[::-1][:3]
        important_features = [_feature_columns[i] for i in top_idx]
    else:
        important_features = _feature_columns[:3]

    return severity, confidence, important_features


def explain_prediction(record: Dict) -> Dict:
    """
    Runs SHAP TreeExplainer on the trained model for a single record and
    returns per-feature contribution toward the predicted class, plus a
    plain-language summary. Falls back to model feature_importances_ if
    SHAP is unavailable in the environment.
    """
    _ensure_loaded()
    X = record_to_feature_row(record)[_feature_columns]

    proba = _model.predict_proba(X)[0]
    pred_idx = int(np.argmax(proba))
    severity = _label_encoder.inverse_transform([pred_idx])[0]
    confidence = float(proba[pred_idx])

    try:
        import shap
        global _explainer
        if _explainer is None:
            _explainer = shap.TreeExplainer(_model)

        shap_values = _explainer.shap_values(X)

        # Handle both shap API shapes: list-per-class or (n, features, classes)
        if isinstance(shap_values, list):
            class_shap = shap_values[pred_idx][0]
            base_value = _explainer.expected_value[pred_idx]
        else:
            arr = np.array(shap_values)
            if arr.ndim == 3:
                class_shap = arr[0, :, pred_idx]
                base_value = (
                    _explainer.expected_value[pred_idx]
                    if hasattr(_explainer.expected_value, "__len__")
                    else _explainer.expected_value
                )
            else:
                class_shap = arr[0]
                base_value = _explainer.expected_value

        contributions = []
        for col, val, contrib in zip(_feature_columns, X.iloc[0].tolist(), class_shap.tolist()):
            contributions.append({
                "feature": _friendly_feature_name(col),
                "value": str(val),
                "contribution": round(float(contrib), 4),
            })
        contributions.sort(key=lambda c: abs(c["contribution"]), reverse=True)
        contributions = contributions[:8]
        base_value = float(base_value) if base_value is not None else 0.0
        method = "shap"
    except Exception:
        # Fallback: use global feature_importances_ signed by whether the
        # feature value is above/below a naive midpoint. Less precise than
        # SHAP but keeps the endpoint functional if shap isn't installed.
        importances = getattr(_model, "feature_importances_", np.ones(len(_feature_columns)))
        contributions = []
        for col, val, imp in zip(_feature_columns, X.iloc[0].tolist(), importances):
            contributions.append({
                "feature": _friendly_feature_name(col),
                "value": str(val),
                "contribution": round(float(imp) * (1 if val else -0.3), 4),
            })
        contributions.sort(key=lambda c: abs(c["contribution"]), reverse=True)
        contributions = contributions[:8]
        base_value = 0.0
        method = "feature_importance_fallback"

    top_positive = [c["feature"] for c in contributions if c["contribution"] > 0][:4]
    if not top_positive:
        top_positive = [c["feature"] for c in contributions[:3]]

    return {
        "predicted_severity": severity,
        "confidence": confidence,
        "base_value": base_value,
        "contributions": contributions,
        "summary": top_positive,
        "method": method,
    }

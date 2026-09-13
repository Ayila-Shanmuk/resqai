"""
Thin service wrapper around ml/predict.py so API routers don't import the
ml package directly (keeps a clean layering: api -> services -> ml).
"""
from typing import Dict
from ml.predict import predict_severity, explain_prediction, ModelNotTrainedError

__all__ = ["predict_severity", "explain_prediction", "ModelNotTrainedError"]

"""
Train the accident-severity classification model.

DATA DISCLOSURE
----------------
No real-world accident dataset ships with this project. This script generates
a clearly-labeled SYNTHETIC dataset using a fixed random seed and a hand-built
rule-of-thumb (higher speed/impact + bad weather/road/lighting -> higher
severity, with noise). This is for DEMONSTRATION ONLY. The accuracy numbers
printed and saved by this script are NOT real-world accuracy and must never
be presented as such.

TO USE A REAL DATASET
----------------------
Replace `generate_synthetic_dataset()` with a loader that reads your real
accident CSV and produces a dataframe with these raw columns:
    speed, impact_magnitude, num_vehicles, num_occupants, airbag_deployed,
    rollover, weather, road_condition, vehicle_type, lighting_condition,
    road_type, severity
then re-run this script. Nothing else needs to change - preprocessing.py
and predict.py are dataset-agnostic.

Usage:
    python ml/train_model.py
"""
import os
import sys
import json
import numpy as np
import pandas as pd
import joblib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # backend/

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import LabelEncoder

from ml.preprocessing import dataframe_to_features, CATEGORICAL_OPTIONS, SEVERITY_LABELS

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

RANDOM_SEED = 42
N_SAMPLES = 4000

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
FEATURE_COLUMNS_PATH = os.path.join(os.path.dirname(__file__), "feature_columns.pkl")
LABEL_ENCODER_PATH = os.path.join(os.path.dirname(__file__), "label_encoder.pkl")
METRICS_PATH = os.path.join(os.path.dirname(__file__), "metrics.json")
DATASET_PATH = os.path.join(os.path.dirname(__file__), "synthetic_dataset.csv")


def generate_synthetic_dataset(n=N_SAMPLES, seed=RANDOM_SEED) -> pd.DataFrame:
    """
    SYNTHETIC / SAMPLE DATA - clearly labeled as such.
    Builds a plausible but fabricated relationship between accident
    circumstances and severity so the ML pipeline has something to train on
    during development.
    """
    rng = np.random.default_rng(seed)

    speed = rng.normal(60, 25, n).clip(0, 160)
    impact_magnitude = rng.normal(2.5, 1.5, n).clip(0, 12)  # derived g-force-like unit
    num_vehicles = rng.choice([1, 2, 3, 4], n, p=[0.5, 0.35, 0.1, 0.05])
    num_occupants = rng.choice([1, 2, 3, 4, 5], n, p=[0.35, 0.3, 0.15, 0.12, 0.08])
    airbag_deployed = rng.choice([0, 1], n, p=[0.6, 0.4])
    rollover = rng.choice([0, 1], n, p=[0.9, 0.1])

    weather = rng.choice(CATEGORICAL_OPTIONS["weather"], n, p=[0.55, 0.25, 0.1, 0.1])
    road_condition = rng.choice(CATEGORICAL_OPTIONS["road_condition"], n, p=[0.55, 0.25, 0.1, 0.1])
    vehicle_type = rng.choice(CATEGORICAL_OPTIONS["vehicle_type"], n, p=[0.55, 0.2, 0.15, 0.1])
    lighting_condition = rng.choice(CATEGORICAL_OPTIONS["lighting_condition"], n, p=[0.5, 0.15, 0.25, 0.1])
    road_type = rng.choice(CATEGORICAL_OPTIONS["road_type"], n, p=[0.5, 0.3, 0.2])

    df = pd.DataFrame({
        "speed": speed,
        "impact_magnitude": impact_magnitude,
        "num_vehicles": num_vehicles,
        "num_occupants": num_occupants,
        "airbag_deployed": airbag_deployed,
        "rollover": rollover,
        "weather": weather,
        "road_condition": road_condition,
        "vehicle_type": vehicle_type,
        "lighting_condition": lighting_condition,
        "road_type": road_type,
    })

    # Hand-built risk score driving the (synthetic) ground-truth severity label
    risk = (
        0.035 * df["speed"]
        + 0.55 * df["impact_magnitude"]
        + 0.35 * df["num_vehicles"]
        + 0.15 * df["num_occupants"]
        - 0.9 * df["airbag_deployed"]
        + 1.6 * df["rollover"]
        + df["weather"].map({"Clear": 0, "Rain": 0.6, "Fog": 0.8, "Storm": 1.3})
        + df["road_condition"].map({"Dry": 0, "Wet": 0.5, "Icy": 1.2, "Damaged": 0.9})
        + df["lighting_condition"].map({"Daylight": 0, "Dusk": 0.3, "Night": 0.7, "Poor": 1.0})
        + df["road_type"].map({"City": 0.2, "Highway": 0.6, "Rural": 0.4})
        + rng.normal(0, 1.1, n)  # noise
    )

    # Bucket the continuous risk score into 4 severity classes
    q1, q2, q3 = np.quantile(risk, [0.45, 0.75, 0.93])
    severity = pd.cut(
        risk,
        bins=[-np.inf, q1, q2, q3, np.inf],
        labels=SEVERITY_LABELS,
    ).astype(str)

    df["severity"] = severity
    return df


def train():
    print("=" * 70)
    print("ResQAI - Accident Severity Model Training")
    print("DATA SOURCE: synthetic/sample dataset (NOT real-world data)")
    print("=" * 70)

    df = generate_synthetic_dataset()
    df.to_csv(DATASET_PATH, index=False)
    print(f"Synthetic dataset saved to {DATASET_PATH} ({len(df)} rows)")

    X = dataframe_to_features(df)
    label_encoder = LabelEncoder()
    label_encoder.fit(SEVERITY_LABELS)
    y = label_encoder.transform(df["severity"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )

    candidates = {}

    rf = RandomForestClassifier(
        n_estimators=200, max_depth=10, random_state=RANDOM_SEED, class_weight="balanced"
    )
    rf.fit(X_train, y_train)
    candidates["RandomForest"] = rf

    if XGBOOST_AVAILABLE:
        xgb = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            random_state=RANDOM_SEED,
            eval_metric="mlogloss",
        )
        xgb.fit(X_train, y_train)
        candidates["XGBoost"] = xgb
    else:
        print("xgboost not installed - training RandomForest only. "
              "Install xgboost to also compare an XGBoost model.")

    results = {}
    for name, model in candidates.items():
        preds = model.predict(X_test)
        results[name] = {
            "accuracy": round(accuracy_score(y_test, preds), 4),
            "precision": round(precision_score(y_test, preds, average="weighted", zero_division=0), 4),
            "recall": round(recall_score(y_test, preds, average="weighted", zero_division=0), 4),
            "f1_score": round(f1_score(y_test, preds, average="weighted", zero_division=0), 4),
        }
        print(f"\n{name}:")
        for k, v in results[name].items():
            print(f"  {k}: {v}")

    best_name = max(results, key=lambda n: results[n]["f1_score"])
    best_model = candidates[best_name]
    print(f"\nSelected best model: {best_name} (highest weighted F1 on held-out test set)")

    joblib.dump(best_model, MODEL_PATH)
    joblib.dump(list(X.columns), FEATURE_COLUMNS_PATH)
    joblib.dump(label_encoder, LABEL_ENCODER_PATH)

    metrics_out = {
        "trained_on": "synthetic_dataset.csv (NOT real-world data)",
        "n_samples": len(df),
        "selected_model": best_name,
        "results": results,
    }
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics_out, f, indent=2)

    print(f"\nModel saved to {MODEL_PATH}")
    print(f"Feature columns saved to {FEATURE_COLUMNS_PATH}")
    print(f"Metrics saved to {METRICS_PATH}")
    print("\nReminder: these metrics reflect a synthetic dataset only.")


if __name__ == "__main__":
    train()

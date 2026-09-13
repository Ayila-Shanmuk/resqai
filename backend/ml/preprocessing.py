"""
Preprocessing utilities shared by training and inference.

Encodes the categorical accident-context fields into the numeric feature
vector the model expects, and defines the canonical feature column order.
This module is the single source of truth for feature engineering so that
train_model.py and predict.py can never drift out of sync with each other.
"""
from typing import Dict
import pandas as pd

# Canonical column order the model is trained and served on.
FEATURE_COLUMNS = [
    "speed",
    "impact_magnitude",
    "num_vehicles",
    "num_occupants",
    "airbag_deployed",
    "rollover",
    "weather_Clear",
    "weather_Rain",
    "weather_Fog",
    "weather_Storm",
    "road_condition_Dry",
    "road_condition_Wet",
    "road_condition_Icy",
    "road_condition_Damaged",
    "vehicle_type_Car",
    "vehicle_type_Bike",
    "vehicle_type_Truck",
    "vehicle_type_Bus",
    "lighting_condition_Daylight",
    "lighting_condition_Dusk",
    "lighting_condition_Night",
    "lighting_condition_Poor",
    "road_type_City",
    "road_type_Highway",
    "road_type_Rural",
]

CATEGORICAL_OPTIONS = {
    "weather": ["Clear", "Rain", "Fog", "Storm"],
    "road_condition": ["Dry", "Wet", "Icy", "Damaged"],
    "vehicle_type": ["Car", "Bike", "Truck", "Bus"],
    "lighting_condition": ["Daylight", "Dusk", "Night", "Poor"],
    "road_type": ["City", "Highway", "Rural"],
}

SEVERITY_LABELS = ["Low", "Moderate", "High", "Critical"]


def record_to_feature_row(record: Dict) -> pd.DataFrame:
    """
    Convert a single raw input dict (as received from the API / dataset row)
    into a one-hot-encoded row matching FEATURE_COLUMNS exactly.
    """
    row = {col: 0 for col in FEATURE_COLUMNS}
    row["speed"] = float(record.get("speed", 0))
    row["impact_magnitude"] = float(record.get("impact_magnitude", 0))
    row["num_vehicles"] = int(record.get("num_vehicles", 1))
    row["num_occupants"] = int(record.get("num_occupants", 1))
    row["airbag_deployed"] = int(bool(record.get("airbag_deployed", False)))
    row["rollover"] = int(bool(record.get("rollover", False)))

    for field, options in CATEGORICAL_OPTIONS.items():
        chosen = record.get(field, options[0])
        col_name = f"{field}_{chosen}"
        if col_name in row:
            row[col_name] = 1
        else:
            # Unknown category value: fall back to the first/default option
            row[f"{field}_{options[0]}"] = 1

    return pd.DataFrame([row], columns=FEATURE_COLUMNS)


def dataframe_to_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Vectorized version of record_to_feature_row for a whole training dataframe.
    Expects raw columns: speed, impact_magnitude, num_vehicles, num_occupants,
    airbag_deployed, rollover, weather, road_condition, vehicle_type,
    lighting_condition, road_type.
    """
    out = pd.DataFrame(0, index=df.index, columns=FEATURE_COLUMNS)
    out["speed"] = df["speed"].astype(float)
    out["impact_magnitude"] = df["impact_magnitude"].astype(float)
    out["num_vehicles"] = df["num_vehicles"].astype(int)
    out["num_occupants"] = df["num_occupants"].astype(int)
    out["airbag_deployed"] = df["airbag_deployed"].astype(int)
    out["rollover"] = df["rollover"].astype(int)

    for field, options in CATEGORICAL_OPTIONS.items():
        for opt in options:
            col_name = f"{field}_{opt}"
            out[col_name] = (df[field] == opt).astype(int)

    return out[FEATURE_COLUMNS]

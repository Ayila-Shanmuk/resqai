"""
Rule-based accident detection from raw sensor readings.

This is intentionally rule-based (not ML) because the raw sensor stream needs
a fast, cheap, always-available first pass to decide whether the situation is
even worth handing to the (heavier) severity ML model. Thresholds are
reasonable defaults for demo purposes and should be tuned against real device
data before any production use.
"""
import math
from typing import Dict

# Thresholds (tune these against real accelerometer/gyroscope data).
# Resting/normal driving sits around 9.8 m/s^2 combined magnitude (gravity)
# and near-zero rad/s, so anything below SUSPICIOUS_* is treated as normal.
SUSPICIOUS_ACCEL_THRESHOLD = 22.0     # m/s^2 combined magnitude
ACCIDENT_ACCEL_THRESHOLD = 30.0

SUSPICIOUS_GYRO_THRESHOLD = 4.0       # rad/s combined magnitude
ACCIDENT_GYRO_THRESHOLD = 6.0

SUDDEN_DECEL_SPEED_DROP = 40.0       # km/h - large instantaneous speed drop is suspicious


def _magnitude(x: float, y: float, z: float) -> float:
    return math.sqrt(x ** 2 + y ** 2 + z ** 2)


def detect_from_sensors(data: Dict, previous_speed: float = None) -> Dict:
    """
    data: dict with accelerometer_x/y/z, gyroscope_x/y/z, speed, latitude, longitude
    Returns a dict: status, impact_magnitude, rotation_magnitude, reason
    """
    accel_mag = _magnitude(
        data["accelerometer_x"], data["accelerometer_y"], data["accelerometer_z"]
    )
    gyro_mag = _magnitude(
        data["gyroscope_x"], data["gyroscope_y"], data["gyroscope_z"]
    )
    speed = data.get("speed", 0)

    reasons = []
    score = 0

    if accel_mag >= ACCIDENT_ACCEL_THRESHOLD:
        score += 2
        reasons.append(f"very high impact force detected ({accel_mag:.1f} m/s\u00b2)")
    elif accel_mag >= SUSPICIOUS_ACCEL_THRESHOLD:
        score += 1
        reasons.append(f"elevated impact force detected ({accel_mag:.1f} m/s\u00b2)")

    if gyro_mag >= ACCIDENT_GYRO_THRESHOLD:
        score += 2
        reasons.append(f"severe rotational motion detected ({gyro_mag:.1f} rad/s)")
    elif gyro_mag >= SUSPICIOUS_GYRO_THRESHOLD:
        score += 1
        reasons.append(f"unusual rotational motion detected ({gyro_mag:.1f} rad/s)")

    if previous_speed is not None and (previous_speed - speed) >= SUDDEN_DECEL_SPEED_DROP:
        score += 2
        reasons.append(f"sudden speed drop from {previous_speed:.0f} to {speed:.0f} km/h")

    if score >= 3:
        status = "possible_accident"
    elif score >= 1:
        status = "suspicious"
    else:
        status = "normal"
        reasons.append("sensor readings within normal driving range")

    return {
        "status": status,
        "impact_magnitude": round(accel_mag, 2),
        "rotation_magnitude": round(gyro_mag, 2),
        "reason": "; ".join(reasons),
    }

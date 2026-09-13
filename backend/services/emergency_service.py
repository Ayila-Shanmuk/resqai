"""
Emergency alert abstraction.

This module builds the emergency message and "sends" it through a pluggable
channel. Only a SIMULATED channel is implemented out of the box - no SMS/
email/call is actually placed unless a real provider is wired in below. This
matches the project requirement to never claim emergency services were
contacted unless a real service is configured.

TO ADD A REAL PROVIDER (e.g. Twilio SMS):
    1. Add credentials to .env (e.g. TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER)
    2. Implement a new `_send_via_twilio(message, to_number)` function here
    3. In `send_emergency_alert`, branch on an env flag such as
       ALERT_CHANNEL=twilio to call it instead of `_send_simulated`
"""
import os
from datetime import datetime, timezone
from typing import Optional, Dict

ALERT_CHANNEL = os.getenv("ALERT_CHANNEL", "simulated")  # simulated | (future: twilio, sendgrid, ...)


def build_alert_message(severity: str, latitude: Optional[float], longitude: Optional[float],
                         timestamp: Optional[datetime] = None) -> str:
    ts = (timestamp or datetime.now(timezone.utc)).strftime("%Y-%m-%d %H:%M:%S UTC")
    if latitude is not None and longitude is not None:
        location_str = f"{latitude:.5f}, {longitude:.5f}"
        map_link = f"https://www.google.com/maps?q={latitude},{longitude}"
    else:
        location_str = "location unavailable"
        map_link = "N/A"

    return (
        f"Emergency Alert: A possible {severity.upper()} severity road accident has been "
        f"detected. Location: {location_str}. Map: {map_link}. Time: {ts}. "
        f"Please check immediately."
    )


def _send_simulated(message: str, accident_id: int) -> Dict:
    """No real network call - logs the alert as sent in SIMULATION mode."""
    return {
        "alert_sent": True,
        "simulated": True,
        "channel": "simulated",
    }


def send_emergency_alert(severity: str, latitude: Optional[float], longitude: Optional[float],
                          accident_id: int, message_override: Optional[str] = None) -> Dict:
    message = message_override or build_alert_message(severity, latitude, longitude)

    if ALERT_CHANNEL == "simulated" or not ALERT_CHANNEL:
        result = _send_simulated(message, accident_id)
    else:
        # Placeholder for real providers - falls back to simulated if not implemented
        result = _send_simulated(message, accident_id)

    result["message"] = message
    result["sent_at"] = datetime.now(timezone.utc)
    return result

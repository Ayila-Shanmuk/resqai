"""
Pydantic request/response schemas used by the API layer.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# ---------- Auth / User ----------

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    phone: str
    emergency_contact_name: Optional[str] = None
    emergency_contact: str
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    emergency_contact_name: Optional[str] = None
    emergency_contact: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


# ---------- Sensor / Detection ----------

class SensorInput(BaseModel):
    accelerometer_x: float
    accelerometer_y: float
    accelerometer_z: float
    gyroscope_x: float
    gyroscope_y: float
    gyroscope_z: float
    speed: float = Field(ge=0, description="Speed in km/h")
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class DetectionResponse(BaseModel):
    status: str  # normal | suspicious | possible_accident
    impact_magnitude: float
    rotation_magnitude: float
    reason: str
    accident_id: Optional[int] = None


# ---------- Severity Prediction ----------

class SeverityInput(BaseModel):
    speed: float = Field(ge=0)
    impact_magnitude: float = Field(ge=0)
    weather: str = "Clear"          # Clear | Rain | Fog | Storm
    road_condition: str = "Dry"     # Dry | Wet | Icy | Damaged
    vehicle_type: str = "Car"       # Car | Bike | Truck | Bus
    lighting_condition: str = "Daylight"  # Daylight | Dusk | Night | Poor
    road_type: str = "City"         # City | Highway | Rural
    num_vehicles: int = Field(default=1, ge=1)
    num_occupants: int = Field(default=1, ge=1)
    airbag_deployed: bool = False
    rollover: bool = False
    accident_id: Optional[int] = None


class SeverityResponse(BaseModel):
    severity: str
    confidence: float
    important_features: List[str]
    accident_id: Optional[int] = None


class ExplainRequest(BaseModel):
    accident_id: Optional[int] = None
    features: SeverityInput


class FeatureContribution(BaseModel):
    feature: str
    value: str
    contribution: float  # positive pushes severity up, negative pushes it down


class ExplainResponse(BaseModel):
    predicted_severity: str
    confidence: float
    base_value: float
    contributions: List[FeatureContribution]
    summary: List[str]
    disclaimer: str = (
        "This explanation shows which factors most influenced the model's "
        "prediction (feature contribution). It does not establish causation."
    )


# ---------- Location ----------

class LocationUpdate(BaseModel):
    latitude: float
    longitude: float
    speed: Optional[float] = None


class AccidentLocation(BaseModel):
    accident_id: int
    latitude: float
    longitude: float


# ---------- Hospitals ----------

class Hospital(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    distance_km: float
    phone: Optional[str] = None
    is_mock_data: bool = True


# ---------- Emergency ----------

class EmergencyAlertRequest(BaseModel):
    accident_id: int
    severity: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    message_override: Optional[str] = None


class EmergencyAlertResponse(BaseModel):
    accident_id: int
    alert_sent: bool
    simulated: bool
    message: str
    sent_at: datetime
    channel: str


class ConfirmSafeRequest(BaseModel):
    accident_id: int


# ---------- Accident history ----------

class AccidentRecord(BaseModel):
    id: int
    timestamp: datetime
    latitude: Optional[float]
    longitude: Optional[float]
    speed: Optional[float]
    detection_status: str
    severity: Optional[str]
    confidence: Optional[float]
    status: str
    hospital: Optional[str]
    emergency_alert_sent: bool
    is_simulated: bool

    class Config:
        from_attributes = True

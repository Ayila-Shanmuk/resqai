"""
SQLAlchemy ORM models: User, Accident, SensorData.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    accidents = relationship("Accident", back_populates="user", cascade="all, delete-orphan")


class Accident(Base):
    __tablename__ = "accidents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)

    detection_status = Column(String, default="normal")  # normal | suspicious | possible_accident
    severity = Column(String, nullable=True)  # Low | Moderate | High | Critical
    confidence = Column(Float, nullable=True)

    status = Column(String, default="pending")  # pending | confirmed | false_alarm | resolved
    hospital = Column(String, nullable=True)
    emergency_alert_sent = Column(Boolean, default=False)
    is_simulated = Column(Boolean, default=False)

    explanation_json = Column(Text, nullable=True)  # cached SHAP explanation

    user = relationship("User", back_populates="accidents")
    sensor_readings = relationship("SensorData", back_populates="accident", cascade="all, delete-orphan")


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    accident_id = Column(Integer, ForeignKey("accidents.id"), nullable=True)

    accelerometer_x = Column(Float, nullable=True)
    accelerometer_y = Column(Float, nullable=True)
    accelerometer_z = Column(Float, nullable=True)
    gyroscope_x = Column(Float, nullable=True)
    gyroscope_y = Column(Float, nullable=True)
    gyroscope_z = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)

    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    accident = relationship("Accident", back_populates="sensor_readings")

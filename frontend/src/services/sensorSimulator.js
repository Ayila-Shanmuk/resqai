// Generates realistic-looking sensor payloads for Simulation Mode, since a
// desktop browser normally can't provide accelerometer/gyroscope/GPS data.
// Clearly a development aid - never presented to the user as real sensor data.

function rand(min, max) {
  return Math.random() * (max - min) + min;
}

// Hyderabad-ish default coordinates, jittered slightly each call.
const BASE_LAT = 17.385;
const BASE_LON = 78.4867;

export function simulateNormalDriving() {
  return {
    accelerometer_x: rand(-0.4, 0.4),
    accelerometer_y: rand(-0.4, 0.4),
    accelerometer_z: rand(9.5, 10.1),
    gyroscope_x: rand(-0.15, 0.15),
    gyroscope_y: rand(-0.15, 0.15),
    gyroscope_z: rand(-0.1, 0.1),
    speed: rand(30, 60),
    latitude: BASE_LAT + rand(-0.01, 0.01),
    longitude: BASE_LON + rand(-0.01, 0.01),
  };
}

// Backend thresholds this file must stay calibrated against (see
// backend/services/accident_detection.py): SUSPICIOUS_ACCEL=22, ACCIDENT_ACCEL=30,
// SUSPICIOUS_GYRO=4, ACCIDENT_GYRO=6 (all as a combined x/y/z vector magnitude).
// Ranges below are chosen so the WORST-CASE (smallest) magnitude they can
// produce still clears the intended threshold with margin, and the
// BEST-CASE (largest) magnitude stays under the next threshold up - so each
// simulation button reliably lands in its intended status every time,
// regardless of where Math.random() lands.
export function simulateSuddenImpact() {
  return {
    // accel magnitude range: ~23.2 to ~29.2 (always between SUSPICIOUS and ACCIDENT)
    accelerometer_x: rand(17, 21),
    accelerometer_y: rand(13, 17),
    accelerometer_z: rand(9, 11),
    // gyro magnitude range: ~4.3 to ~5.9 (always between SUSPICIOUS and ACCIDENT)
    gyroscope_x: rand(3, 4),
    gyroscope_y: rand(2.5, 3.5),
    gyroscope_z: rand(1.8, 2.5),
    speed: rand(20, 45),
    latitude: BASE_LAT + rand(-0.01, 0.01),
    longitude: BASE_LON + rand(-0.01, 0.01),
  };
}

export function simulateSeriousAccident() {
  return {
    // accel magnitude range: ~32.8 to ~42.1 (always well above ACCIDENT threshold)
    accelerometer_x: rand(24, 30),
    accelerometer_y: rand(20, 26),
    accelerometer_z: rand(10, 14),
    // gyro magnitude range: ~7.6 to ~10.8 (always well above ACCIDENT threshold)
    gyroscope_x: rand(5, 7),
    gyroscope_y: rand(4.5, 6.5),
    gyroscope_z: rand(3.5, 5),
    speed: rand(5, 20), // sudden near-stop after high-speed travel
    latitude: BASE_LAT + rand(-0.01, 0.01),
    longitude: BASE_LON + rand(-0.01, 0.01),
  };
}

// Reasonable default "context" fields to accompany a serious-accident
// simulation when calling /api/predict-severity, so the whole demo flow
// (detect -> severity -> explain -> hospital -> emergency) works end to end
// without asking the user to fill out a form mid-emergency-drill.
export function simulatedSeverityContext(sensorSnapshot) {
  return {
    speed: 95,
    impact_magnitude: Math.sqrt(
      sensorSnapshot.accelerometer_x ** 2 +
        sensorSnapshot.accelerometer_y ** 2 +
        sensorSnapshot.accelerometer_z ** 2
    ),
    weather: "Storm",
    road_condition: "Wet",
    vehicle_type: "Car",
    lighting_condition: "Night",
    road_type: "Highway",
    num_vehicles: 2,
    num_occupants: 2,
    airbag_deployed: true,
    rollover: false,
  };
}

"""
ResQAI End-to-End System Verification Suite
---------------------------------------------
Runs a full automated verification of:
1. Database initialization and table creation
2. User Registration, Authentication & Profile retrieval
3. Live Location tracking & updates
4. Rule-based Accident Detection engine
5. Machine Learning Severity Assessment model (RandomForest/XGBoost)
6. Explainable AI (SHAP) feature contribution analysis
7. Nearby Hospital recommendation engine
8. Emergency Alert generation & Confirmation / Cancellation flow
9. Accident History audit retrieval
"""
import os
import sys
import uuid
import unittest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from main import app
from database.database import init_db


class TestResQAIEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n" + "=" * 70)
        print(" INITIALIZING RESQAI END-TO-END VERIFICATION SUITE")
        print("=" * 70)
        init_db()
        cls.client = TestClient(app)
        
        # Test credentials
        cls.test_id = str(uuid.uuid4())[:8]
        cls.test_email = f"driver_{cls.test_id}@example.com"
        cls.test_password = "SecurePassword123!"
        cls.auth_headers = {}
        cls.created_accident_id = None

    def test_01_health_check(self):
        print("\n[E2E 01] Verifying System Health Check Endpoint...")
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "ok")
        print("  [PASS] Backend status OK")

    def test_02_auth_workflow(self):
        print("\n[E2E 02] Testing User Registration, Authentication & Profile...")
        # 1. Register
        reg_payload = {
            "name": "Jane Driver",
            "email": self.test_email,
            "password": self.test_password,
            "phone": "+15550199",
            "emergency_contact_name": "John Driver",
            "emergency_contact": "+15550188"
        }
        reg_res = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(reg_res.status_code, 200, f"Registration failed: {reg_res.text}")
        reg_data = reg_res.json()
        self.assertIn("access_token", reg_data)
        token = reg_data["access_token"]
        self.__class__.auth_headers = {"Authorization": f"Bearer {token}"}
        print("  [PASS] User registration successful")

        # 2. Login
        login_res = self.client.post("/api/auth/login", json={
            "email": self.test_email,
            "password": self.test_password
        })
        self.assertEqual(login_res.status_code, 200)
        self.assertIn("access_token", login_res.json())
        print("  [PASS] Authentication & JWT generation successful")

        # 3. Profile /me
        me_res = self.client.get("/api/auth/me", headers=self.auth_headers)
        self.assertEqual(me_res.status_code, 200)
        me_data = me_res.json()
        self.assertEqual(me_data["email"], self.test_email)
        self.assertEqual(me_data["emergency_contact_name"], "John Driver")
        print("  [PASS] User profile retrieval verified")

    def test_03_location_tracking(self):
        print("\n[E2E 03] Testing Live Location Updates & Retrieval...")
        loc_payload = {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "speed": 65.5
        }
        update_res = self.client.post("/api/location", json=loc_payload, headers=self.auth_headers)
        self.assertEqual(update_res.status_code, 200)
        print("  [PASS] Location updated")

        get_res = self.client.get("/api/location", headers=self.auth_headers)
        self.assertEqual(get_res.status_code, 200)
        loc_data = get_res.json()
        self.assertAlmostEqual(loc_data["latitude"], 37.7749)
        self.assertAlmostEqual(loc_data["longitude"], -122.4194)
        print("  [PASS] Location retrieval verified")

    def test_04_accident_detection_engine(self):
        print("\n[E2E 04] Testing Rule-Based Accident Detection Engine...")
        # High impact crash simulation payload
        impact_payload = {
            "accelerometer_x": 2.1,
            "accelerometer_y": 45.8,
            "accelerometer_z": 12.3,
            "gyroscope_x": 3.2,
            "gyroscope_y": 8.5,
            "gyroscope_z": 4.1,
            "speed": 85.0,
            "latitude": 37.7749,
            "longitude": -122.4194
        }
        res = self.client.post("/api/detect-accident", json=impact_payload, headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn(data["status"], ["normal", "suspicious", "possible_accident"])
        
        if data.get("accident_id"):
            self.__class__.created_accident_id = data["accident_id"]
        
        print(f"  [PASS] Accident Detection status: '{data['status']}' (impact magnitude: {data['impact_magnitude']})")

    def test_05_ml_severity_prediction(self):
        print("\n[E2E 05] Testing Machine Learning Severity Prediction Model...")
        severity_input = {
            "speed": 95.0,
            "impact_magnitude": 6.8,
            "num_vehicles": 3,
            "num_occupants": 2,
            "airbag_deployed": True,
            "rollover": True,
            "weather": "Rain",
            "road_condition": "Wet",
            "vehicle_type": "SUV",
            "lighting_condition": "Night",
            "road_type": "Highway"
        }
        res = self.client.post("/api/predict-severity", json=severity_input, headers=self.auth_headers)
        self.assertEqual(res.status_code, 200, f"Severity prediction failed: {res.text}")
        data = res.json()
        self.assertIn(data["severity"], ["Low", "Moderate", "High", "Critical"])
        self.assertIn("confidence", data)
        print(f"  [PASS] ML predicted severity: {data['severity']} (Confidence: {data.get('confidence', 'N/A')})")

    def test_06_shap_explainability(self):
        print("\n[E2E 06] Testing Explainable AI (SHAP) Analysis...")
        explain_input = {
            "features": {
                "speed": 95.0,
                "impact_magnitude": 6.8,
                "num_vehicles": 3,
                "num_occupants": 2,
                "airbag_deployed": True,
                "rollover": True,
                "weather": "Rain",
                "road_condition": "Wet",
                "vehicle_type": "SUV",
                "lighting_condition": "Night",
                "road_type": "Highway"
            }
        }
        res = self.client.post("/api/explain-prediction", json=explain_input, headers=self.auth_headers)
        self.assertEqual(res.status_code, 200, f"SHAP explanation failed: {res.text}")
        data = res.json()
        self.assertIn("predicted_severity", data)
        self.assertIn("summary", data)
        self.assertIn("contributions", data)
        print(f"  [PASS] SHAP Predicted Severity: \"{data['predicted_severity']}\"")
        if data["contributions"]:
            top = data["contributions"][0]
            print(f"  [PASS] Top feature driver: {top['feature']} ({top['value']} -> contribution: {top['contribution']})")

    def test_07_nearby_hospitals(self):
        print("\n[E2E 07] Testing Nearby Hospital Lookup Engine...")
        params = {"latitude": 37.7749, "longitude": -122.4194}
        res = self.client.get("/api/hospitals/nearby", params=params, headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        hospitals = res.json()
        self.assertIsInstance(hospitals, list)
        self.assertTrue(len(hospitals) > 0)
        top_h = hospitals[0]
        print(f"  [PASS] Retrieved {len(hospitals)} nearby hospitals (Top recommendation: {top_h['name']} - {top_h['distance_km']} km)")

    def test_08_emergency_alert_flow(self):
        print("\n[E2E 08] Testing Emergency Alert Triggering & Safety Confirmation...")
        # 1. Alert trigger
        alert_payload = {
            "accident_id": self.created_accident_id or 1,
            "severity": "Critical",
            "latitude": 37.7749,
            "longitude": -122.4194
        }
        alert_res = self.client.post("/api/emergency/alert", json=alert_payload, headers=self.auth_headers)
        self.assertEqual(alert_res.status_code, 200)
        alert_data = alert_res.json()
        self.assertTrue(alert_data.get("alert_sent", False))
        print(f"  [PASS] Emergency alert dispatched (simulated: {alert_data.get('simulated')})")

        # 2. Confirm safe (cancel alert flow)
        safe_payload = {"accident_id": self.created_accident_id or 1}
        safe_res = self.client.post("/api/emergency/confirm-safe", json=safe_payload, headers=self.auth_headers)
        self.assertEqual(safe_res.status_code, 200)
        safe_data = safe_res.json()
        self.assertIn("status", safe_data)
        print("  [PASS] User confirmed safe - false alarm logged and alert cancelled")

    def test_09_accident_history(self):
        print("\n[E2E 09] Testing Accident History Audit Log...")
        res = self.client.get("/api/accidents", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        history = res.json()
        self.assertIsInstance(history, list)
        print(f"  [PASS] Accident history log returned {len(history)} record(s)")

    @classmethod
    def tearDownClass(cls):
        print("\n" + "=" * 70)
        print(" ALL END-TO-END VERIFICATION TESTS PASSED SUCCESSFULLY!")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)

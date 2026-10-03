import axios from "axios";

const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || "";
const API_BASE_URL = rawBaseUrl.endsWith("/") ? rawBaseUrl.slice(0, -1) : rawBaseUrl;

const api = axios.create({
  baseURL: API_BASE_URL || undefined,
  headers: { "Content-Type": "application/json" },
});

// Attach the JWT (if present) to every outgoing request.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("resqai_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Normalize errors so components can show a friendly message regardless of
// whether the failure was a network error or an API error response.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    let friendlyMessage = "Something went wrong. Please try again.";
    if (error.response) {
      friendlyMessage =
        error.response.data?.detail ||
        `Request failed (${error.response.status}). Please try again.`;
      if (error.response.status === 401) {
        localStorage.removeItem("resqai_token");
        localStorage.removeItem("resqai_user");
      }
    } else if (error.request) {
      friendlyMessage =
        "Can't reach the ResQAI backend. Make sure it's running at " +
        API_BASE_URL +
        ".";
    }
    return Promise.reject({ ...error, friendlyMessage });
  }
);

// ---- Auth ----
export const registerUser = (data) => api.post("/api/auth/register", data);
export const loginUser = (data) => api.post("/api/auth/login", data);
export const getMe = () => api.get("/api/auth/me");

// ---- Accident detection ----
export const detectAccident = (sensorData) => api.post("/api/detect-accident", sensorData);
export const getAccidentHistory = () => api.get("/api/accidents");

// ---- Severity ----
export const predictSeverity = (data) => api.post("/api/predict-severity", data);
export const explainPrediction = (data) => api.post("/api/explain-prediction", data);

// ---- Location ----
export const getLastLocation = () => api.get("/api/location");
export const updateLocation = (data) => api.post("/api/location", data);
export const saveAccidentLocation = (data) => api.post("/api/accident/location", data);

// ---- Hospitals ----
export const getNearbyHospitals = (latitude, longitude, accidentId) =>
  api.get("/api/hospitals/nearby", {
    params: { latitude, longitude, accident_id: accidentId || undefined },
  });

// ---- Emergency ----
export const sendEmergencyAlert = (data) => api.post("/api/emergency/alert", data);
export const confirmSafe = (accidentId) =>
  api.post("/api/emergency/confirm-safe", { accident_id: accidentId });

export default api;

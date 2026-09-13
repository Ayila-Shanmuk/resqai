"""
Nearby-hospital lookup service.

If GOOGLE_MAPS_API_KEY is configured in .env, this service calls the Google
Places API "nearbysearch" endpoint. Otherwise it falls back to a clearly
labeled MOCK dataset so the feature is demonstrable without any API key or
network access. Mock data is never presented to the frontend as if it were
real.
"""
import os
import math
from typing import List, Dict
import httpx

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# Clearly-labeled MOCK hospital data for development / offline demo use.
# Coordinates are illustrative offsets around whatever point is queried.
MOCK_HOSPITAL_TEMPLATES = [
    {"name": "City General Hospital", "phone": "+91-40-1234-5678", "offset": (0.01, 0.01)},
    {"name": "St. Mary's Emergency Center", "phone": "+91-40-2345-6789", "offset": (-0.015, 0.008)},
    {"name": "Sunrise Multi-Specialty Hospital", "phone": "+91-40-3456-7890", "offset": (0.008, -0.02)},
    {"name": "Metro Trauma & Accident Care", "phone": "+91-40-4567-8901", "offset": (-0.02, -0.012)},
    {"name": "Lakeview Community Hospital", "phone": "+91-40-5678-9012", "offset": (0.022, 0.005)},
]


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _mock_hospitals(latitude: float, longitude: float) -> List[Dict]:
    hospitals = []
    for tmpl in MOCK_HOSPITAL_TEMPLATES:
        h_lat = latitude + tmpl["offset"][0]
        h_lon = longitude + tmpl["offset"][1]
        hospitals.append({
            "name": tmpl["name"],
            "address": f"Near {latitude:.4f}, {longitude:.4f} (mock address)",
            "latitude": h_lat,
            "longitude": h_lon,
            "distance_km": round(_haversine_km(latitude, longitude, h_lat, h_lon), 2),
            "phone": tmpl["phone"],
            "is_mock_data": True,
        })
    hospitals.sort(key=lambda h: h["distance_km"])
    return hospitals


async def _google_places_hospitals(latitude: float, longitude: float, radius_m: int = 5000) -> List[Dict]:
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{latitude},{longitude}",
        "radius": radius_m,
        "type": "hospital",
        "key": GOOGLE_MAPS_API_KEY,
    }
    async with httpx.AsyncClient(timeout=8.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    hospitals = []
    for place in data.get("results", []):
        loc = place.get("geometry", {}).get("location", {})
        h_lat, h_lon = loc.get("lat"), loc.get("lng")
        if h_lat is None or h_lon is None:
            continue
        hospitals.append({
            "name": place.get("name", "Unnamed Hospital"),
            "address": place.get("vicinity", "Address unavailable"),
            "latitude": h_lat,
            "longitude": h_lon,
            "distance_km": round(_haversine_km(latitude, longitude, h_lat, h_lon), 2),
            "phone": None,  # Requires a separate Place Details call; omitted to limit API usage
            "is_mock_data": False,
        })
    hospitals.sort(key=lambda h: h["distance_km"])
    return hospitals


async def get_nearby_hospitals(latitude: float, longitude: float) -> List[Dict]:
    if GOOGLE_MAPS_API_KEY:
        try:
            hospitals = await _google_places_hospitals(latitude, longitude)
            if hospitals:
                return hospitals
            # API reachable but returned nothing usable -> fall back to mock
            return _mock_hospitals(latitude, longitude)
        except Exception:
            # Network/API failure -> fall back to mock data rather than error out
            return _mock_hospitals(latitude, longitude)
    return _mock_hospitals(latitude, longitude)

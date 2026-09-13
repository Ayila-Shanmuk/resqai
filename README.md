# ResQAI — AI-Powered Accident Detection & Emergency Response System

ResQAI is a full-stack demo application that detects a possible road accident
from smartphone-style sensor data (accelerometer, gyroscope, speed, GPS),
estimates the accident's severity with a trained machine learning model,
explains that prediction with SHAP, finds a nearby hospital, and walks
through a 10-second confirmation flow before sending a (simulated) emergency
alert to the user's emergency contact.

> **This is a development / academic demo, not a production safety product.**
> Emergency alerts are simulated by default (no real SMS/call is placed
> unless you wire in a real provider), hospital data falls back to clearly
> labeled mock data when no Maps API key is configured, and the ML model is
> trained on a synthetic dataset — see the [Important disclaimers](#important-disclaimers)
> section before demoing or extending this project.

---

## Table of contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Technology stack](#technology-stack)
4. [Folder structure](#folder-structure)
5. [Prerequisites](#prerequisites)
6. [Backend setup](#backend-setup)
7. [ML model training](#ml-model-training)
8. [Frontend setup](#frontend-setup)
9. [Running the full application](#running-the-full-application)
10. [Environment variables](#environment-variables)
11. [API endpoints](#api-endpoints)
12. [How to use Simulation Mode](#how-to-use-simulation-mode)
13. [Replacing the synthetic dataset with a real one](#replacing-the-synthetic-dataset-with-a-real-one)
14. [Troubleshooting](#troubleshooting)
15. [Important disclaimers](#important-disclaimers)

---

## Features

- **User accounts** — registration/login (JWT-based), profile with name,
  phone, and emergency contact.
- **Live dashboard** — safety status (🟢/🟡/🔴), sensor readings, GPS map,
  emergency-contact card, recent accident history.
- **Rule-based accident detection** from accelerometer/gyroscope/speed data
  (`POST /api/detect-accident`), classifying events as `normal`,
  `suspicious`, or `possible_accident`.
- **ML severity prediction** (Random Forest / XGBoost, whichever scores
  higher on held-out data) across four classes: Low, Moderate, High,
  Critical (`POST /api/predict-severity`).
- **Explainable AI** via SHAP feature-contribution analysis, with a
  plain-language summary of the top contributing factors
  (`POST /api/explain-prediction`).
- **10-second accident confirmation screen** — "I'M SAFE" cancels the alert
  and logs a false alarm; letting the countdown hit zero (or tapping "Send
  Emergency Alert Now") triggers the emergency flow.
- **Nearby hospital recommendation**, ranked by distance, with a directions
  button (`GET /api/hospitals/nearby`).
- **Emergency response screen** — severity, location on a map, recommended
  hospital, emergency-contact info, and one-tap actions (call emergency
  services, call emergency contact, open hospital directions, cancel alert).
- **Simulation Mode** — "Simulate Normal Driving / Sudden Impact / Serious
  Accident" buttons so the whole pipeline can be demoed without a real phone.
- **Accident history table** with date, location, severity, detection
  status, and response outcome.

## Architecture

```
┌────────────────────┐        REST/JSON         ┌──────────────────────┐
│   React Frontend    │ ───────────────────────▶ │   FastAPI Backend    │
│  (Vite, port 5173)  │ ◀─────────────────────── │   (Uvicorn, 8000)    │
└────────────────────┘                            └──────────┬───────────┘
                                                               │
                              ┌────────────────────────────────┼─────────────────────────┐
                              │                                │                          │
                     ┌────────▼────────┐             ┌─────────▼─────────┐      ┌─────────▼─────────┐
                     │  SQLite (dev)    │             │  ML pipeline       │      │  External services │
                     │  User/Accident/  │             │  RandomForest /    │      │  Google Places API │
                     │  SensorData      │             │  XGBoost + SHAP    │      │  (or mock fallback) │
                     └──────────────────┘             └────────────────────┘      └─────────────────────┘
```

The backend is layered `api/` → `services/` → `ml/`/`database/`, so routers
never talk to the database or the model directly — they go through a
service function. That keeps each layer swappable (e.g. SQLite → Postgres,
mock hospitals → real Places API) without touching the API contracts.

## Technology stack

**Frontend:** React 18 (Vite), React Router, Axios, plain CSS (custom design
system — no UI kit dependency).

**Backend:** Python, FastAPI, Uvicorn, SQLAlchemy, Pydantic, python-jose +
passlib (JWT auth), httpx.

**Machine learning:** pandas, NumPy, scikit-learn (RandomForest), XGBoost
(optional), SHAP (optional, falls back gracefully), joblib.

**Database:** SQLite for development; the code targets SQLAlchemy only, so
migrating to MySQL/PostgreSQL is a `DATABASE_URL` change (see
[Environment variables](#environment-variables)).

**Maps:** OpenStreetMap embed for map display (no API key needed) and an
optional Google Places API integration for real hospital search.

## Folder structure

```
resqai/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── api/
│   │   ├── auth.py            # register / login / me
│   │   ├── accident.py        # detect-accident, accidents history
│   │   ├── severity.py        # predict-severity, explain-prediction
│   │   ├── hospital.py        # hospitals/nearby
│   │   ├── location.py        # location, accident/location
│   │   └── emergency.py       # emergency/alert, emergency/confirm-safe
│   ├── models/
│   │   ├── database_models.py # User, Accident, SensorData (SQLAlchemy)
│   │   └── schemas.py         # Pydantic request/response schemas
│   ├── services/
│   │   ├── accident_detection.py
│   │   ├── severity_prediction.py
│   │   ├── hospital_service.py
│   │   ├── emergency_service.py
│   │   └── auth_service.py
│   ├── ml/
│   │   ├── train_model.py
│   │   ├── predict.py
│   │   ├── preprocessing.py
│   │   ├── model.pkl                 # generated by train_model.py
│   │   ├── feature_columns.pkl       # generated by train_model.py
│   │   ├── label_encoder.pkl         # generated by train_model.py
│   │   ├── metrics.json              # generated by train_model.py
│   │   └── synthetic_dataset.csv     # generated by train_model.py
│   └── database/
│       └── database.py
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    ├── .env.example
    └── src/
        ├── components/
        │   ├── Navbar.jsx
        │   ├── AccidentStatus.jsx
        │   ├── SensorCard.jsx
        │   ├── MapView.jsx
        │   ├── SeverityCard.jsx
        │   └── HospitalCard.jsx
        ├── pages/
        │   ├── Login.jsx
        │   ├── Register.jsx
        │   ├── Dashboard.jsx
        │   ├── AccidentDetected.jsx
        │   ├── EmergencyResponse.jsx
        │   ├── Hospitals.jsx
        │   └── AccidentHistory.jsx
        ├── services/
        │   ├── api.js
        │   └── sensorSimulator.js
        ├── AuthContext.jsx
        ├── ToastContext.jsx
        ├── App.jsx
        ├── main.jsx
        └── index.css
```

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- No external API keys are required to run the full demo (Simulation Mode +
  mock hospital data + simulated alerts work out of the box).

## Backend setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# edit .env if you want to add a real Google Maps API key, etc.

python ml/train_model.py     # trains and saves the severity model
uvicorn main:app --reload
```

The backend starts at **http://localhost:8000**. Interactive API docs (Swagger)
are at **http://localhost:8000/docs**. On first run, `init_db()` creates
`resqai.db` (SQLite) automatically — no manual migration step needed.

## ML model training

`python ml/train_model.py` will:

1. Generate a **clearly-labeled synthetic dataset** (`ml/synthetic_dataset.csv`,
   4,000 rows) using a fixed random seed and a hand-built risk formula
   (higher speed/impact + bad weather/road/lighting → higher severity, plus
   noise). **This is not real-world accident data.**
2. Train a RandomForest classifier (and an XGBoost classifier too, if
   `xgboost` is installed).
3. Compare them on accuracy, precision, recall, and weighted F1 on a held-out
   test split, and select the better performer.
4. Save `model.pkl`, `feature_columns.pkl`, `label_encoder.pkl`, and
   `metrics.json` into `ml/`.

You should re-run this script any time you change `ml/preprocessing.py` or
swap in a real dataset. The backend will return a `503` from the severity
endpoints with a clear message if you try to use them before training.

## Frontend setup

```bash
cd frontend
npm install
cp .env.example .env
# edit .env only if your backend is not at http://localhost:8000
npm run dev
```

The frontend starts at **http://localhost:5173** and is already configured
to call the backend at the URL in `VITE_API_BASE_URL`.

## Running the full application

Open two terminals:

```bash
# Terminal 1
cd backend
venv\Scripts\activate   # or: source venv/bin/activate
uvicorn main:app --reload

# Terminal 2
cd frontend
npm run dev
```

Then visit **http://localhost:5173**, register an account, and try
**Simulation Mode** on the dashboard.

## Automated End-to-End Verification

ResQAI includes a complete automated system test suite verifying authentication, location tracking, accident detection, ML severity prediction, SHAP explainability, hospital search, emergency alerts, and history logging:

```bash
# Run the full automated verification test suite
python test_e2e.py
```

## Deploying to Render

ResQAI is configured for seamless 1-click deployment to [Render](https://render.com) as a single unified Web Service.

### Quick Start (Render Blueprint)
1. Push this repository to GitHub/GitLab.
2. Go to **Render Dashboard** → **New +** → **Blueprint**.
3. Connect your repository. Render will automatically read `render.yaml` and configure the build and runtime environment.
4. Click **Apply**.

For complete step-by-step instructions, Docker options, and environment variables, see [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md).


## Environment variables

**`backend/.env`** (copy from `backend/.env.example`):

| Variable              | Default                     | Purpose                                                                 |
|-----------------------|------------------------------|--------------------------------------------------------------------------|
| `DATABASE_URL`        | `sqlite:///./resqai.db`      | SQLAlchemy connection string. Swap for a Postgres/MySQL URL to migrate.  |
| `JWT_SECRET_KEY`      | *(dev placeholder)*          | Secret used to sign login tokens. Change this for any real deployment.  |
| `GOOGLE_MAPS_API_KEY` | *(blank)*                    | Optional. If blank, hospital lookup uses clearly-labeled mock data.     |
| `ALERT_CHANNEL`       | `simulated`                  | Emergency alert channel. Only `simulated` is implemented out of the box.|

**`frontend/.env`** (copy from `frontend/.env.example`):

| Variable              | Default                     | Purpose                                  |
|-----------------------|------------------------------|--------------------------------------------|
| `VITE_API_BASE_URL`   | `http://localhost:8000`      | Base URL the frontend calls for the API.   |

Neither `.env` file is committed to source control (`.gitignore` excludes
both) — never hard-code API keys directly in frontend or backend source.

## API endpoints

All endpoints except `/api/auth/register` and `/api/auth/login` require an
`Authorization: Bearer <token>` header. Full interactive schemas are always
available at `/docs`.

| Method | Endpoint                        | Description                                             |
|--------|----------------------------------|-----------------------------------------------------------|
| POST   | `/api/auth/register`             | Create an account, returns a JWT + profile               |
| POST   | `/api/auth/login`                 | Log in, returns a JWT + profile                          |
| GET    | `/api/auth/me`                   | Current user's profile                                    |
| POST   | `/api/detect-accident`           | Submit sensor data → `normal`/`suspicious`/`possible_accident` |
| GET    | `/api/accidents`                 | Current user's accident history                           |
| POST   | `/api/predict-severity`          | Predict severity (Low/Moderate/High/Critical) + confidence |
| POST   | `/api/explain-prediction`        | SHAP-based feature contribution for a severity prediction  |
| GET    | `/api/location`                  | Last known location for the current user                  |
| POST   | `/api/location`                  | Update the current user's live location                   |
| POST   | `/api/accident/location`         | Attach/confirm GPS coordinates to a specific accident      |
| GET    | `/api/hospitals/nearby`          | Nearby hospitals ranked by distance (`?latitude=&longitude=`) |
| POST   | `/api/emergency/alert`           | Trigger the (simulated) emergency alert for an accident    |
| POST   | `/api/emergency/confirm-safe`    | Mark an accident as a false alarm, cancelling the alert     |

## How to use Simulation Mode

1. Register/log in and land on the Dashboard.
2. Use the three buttons under **Simulation Mode**:
   - **Simulate Normal Driving** — generates calm sensor values; status
     stays 🟢 SAFE.
   - **Simulate Sudden Impact** — generates moderately elevated readings;
     status becomes 🟡 POSSIBLE ACCIDENT (suspicious), no confirmation
     screen.
   - **Simulate Serious Accident** — generates a high-impact/high-rotation
     reading; the backend classifies it as `possible_accident`, and the
     frontend opens the 10-second confirmation screen, runs the severity
     model + SHAP explanation in the background, and — if you don't tap
     "I'M SAFE" — proceeds to the Emergency Response screen with a
     recommended hospital and a simulated alert message.
3. Everything generated this way is saved to the Accident History page just
   like a real detection would be.

## Replacing the synthetic dataset with a real dataset

1. Get a real accident dataset with (or mappable to) these raw columns:
   `speed, impact_magnitude, num_vehicles, num_occupants, airbag_deployed,
   rollover, weather, road_condition, vehicle_type, lighting_condition,
   road_type, severity` (severity ∈ `Low, Moderate, High, Critical`).
2. In `backend/ml/train_model.py`, replace the call to
   `generate_synthetic_dataset()` with a loader for your CSV/dataframe that
   produces those same columns.
3. Nothing else needs to change — `preprocessing.py` and `predict.py` are
   dataset-agnostic as long as the raw column names match.
4. Re-run `python ml/train_model.py`. The printed/saved accuracy, precision,
   recall, and F1 will now reflect your real dataset instead of the
   synthetic one.

## Troubleshooting

- **`AttributeError: module 'bcrypt' has no attribute '__about__'` during
  registration** — this was caused by routing password hashing through
  `passlib`'s `CryptContext`, which probes for a `bcrypt.__about__` attribute
  that current `bcrypt` releases removed. Fixed: `services/auth_service.py`
  now calls `bcrypt.hashpw`/`bcrypt.checkpw` directly and `passlib` is no
  longer a dependency at all, so this error class can't recur regardless of
  which `bcrypt` version you have installed.
- **`ModuleNotFoundError` on backend startup** — make sure you activated the
  virtualenv and ran `pip install -r requirements.txt` from inside `backend/`.
- **Severity endpoints return 503** — you haven't trained the model yet; run
  `python ml/train_model.py` from `backend/`.
- **Frontend shows "Can't reach the ResQAI backend"** — confirm
  `uvicorn main:app --reload` is running on port 8000, and that
  `frontend/.env`'s `VITE_API_BASE_URL` matches it.
- **CORS errors in the browser console** — the backend only allows
  `http://localhost:5173` / `http://127.0.0.1:5173` by default (see
  `main.py`'s `CORSMiddleware`); update it if you serve the frontend
  elsewhere.
- **Hospital list looks the same every time** — you have no
  `GOOGLE_MAPS_API_KEY` configured, so the mock hospital generator is
  active by design; every hospital returned that way includes
  `"is_mock_data": true` in the API response.
- **XGBoost/SHAP not installed** — the app degrades gracefully: training
  uses RandomForest only, and `/api/explain-prediction` falls back to a
  feature-importance-based explanation instead of SHAP. Install `xgboost`
  and `shap` (already in `requirements.txt`) and retrain to get both back.
- **Missing GPS on a simulated reading** — the simulator always attaches
  coordinates, but if you extend this to real device sensors and GPS is
  unavailable, `latitude`/`longitude` are optional throughout the API and
  the frontend's `MapView` component shows a friendly "no coordinates yet"
  state instead of crashing.

## Important disclaimers

- **Emergency alerts are simulated.** No SMS, phone call, or third-party
  emergency API is triggered unless you implement a real provider in
  `backend/services/emergency_service.py` and set `ALERT_CHANNEL`
  accordingly. The UI always labels simulated alerts as such.
- **Hospital data is mock data unless a real Maps API key is configured.**
  Mock hospitals are clearly flagged with `is_mock_data: true`.
- **The ML model is trained on a synthetic dataset.** The accuracy/precision/
  recall/F1 numbers in `ml/metrics.json` describe performance on that
  synthetic data only and must not be presented as real-world accuracy.
  See [Replacing the synthetic dataset](#replacing-the-synthetic-dataset-with-a-real-one)
  to train on real data.
- **SHAP explanations describe feature contribution, not causation.** The
  API response includes this disclaimer directly in
  `ExplainResponse.disclaimer`.

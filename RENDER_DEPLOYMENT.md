# ResQAI — Render Deployment Guide

This guide provides step-by-step instructions for deploying the full-stack **ResQAI** application (FastAPI backend + ML RandomForest/SHAP engine + React frontend) to [Render](https://render.com).

---

## Deployment Architecture Overview

ResQAI is configured to build and deploy as a **Single Web Service** on Render:

```
┌────────────────────────────────────────────────────────┐
│               Render Web Service                       │
│                                                        │
│   FastAPI (Uvicorn on $PORT)                           │
│   ├── /api/...                 (Backend API Endpoints) │
│   ├── /docs                    (Swagger Documentation) │
│   └── /* (SPA Static Fallback) (React Frontend Build)  │
└────────────────────────────────────────────────────────┘
```

**Benefits of this setup:**
1. **Free Tier Compatibility:** Fits within Render's 1 free Web Service allocation.
2. **Zero CORS Friction:** Frontend calls `/api/...` directly on the same domain in production.
3. **Automated Model Training:** The ML model (`train_model.py`) is trained automatically during the Render build phase.

---

## Option 1: 1-Click Blueprint Deployment (Recommended)

Render standardizes Infrastructure-as-Code via `render.yaml`.

### Steps:
1. Push your repository (or fork) to **GitHub** or **GitLab**.
2. Log into your [Render Dashboard](https://dashboard.render.com).
3. Click **New +** → Select **Blueprint**.
4. Connect your GitHub/GitLab repository.
5. Render will automatically detect `render.yaml` and configure:
   - **Build Command:** `./build.sh`
   - **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables:** `PYTHON_VERSION=3.11.6`, `NODE_VERSION=20.10.0`, `JWT_SECRET_KEY` (auto-generated), `DATABASE_URL=sqlite:///./resqai.db`, `ALERT_CHANNEL=simulated`.
6. Click **Apply**. Render will trigger the build and deploy your live URL!

---

## Option 2: Manual Web Service Setup on Render Dashboard

If you prefer to manually configure a Web Service:

### Steps:
1. Go to [Render Dashboard](https://dashboard.render.com) → Click **New +** → **Web Service**.
2. Connect your Git repository.
3. Fill in the deployment details:
   - **Name:** `resqai`
   - **Region:** Choose closest to your users (e.g. Oregon, Frankfurt, Singapore).
   - **Branch:** `main` (or your default branch)
   - **Root Directory:** (leave blank)
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```bash
     pip install -r backend/requirements.txt && python backend/ml/train_model.py && cd frontend && npm install && npm run build
     ```
   - **Start Command:**
     ```bash
     cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
4. Environment Variables section:
   - `PYTHON_VERSION`: `3.11.6`
   - `NODE_VERSION`: `20.10.0`
   - `JWT_SECRET_KEY`: (Enter a random 32-character string)
   - `DATABASE_URL`: `sqlite:///./resqai.db`
   - `ALERT_CHANNEL`: `simulated`
   - `GOOGLE_MAPS_API_KEY`: (Optional - leave empty for mock data)
5. Click **Create Web Service**.

---

## Option 3: Docker Deployment on Render

ResQAI includes a production multi-stage `Dockerfile`.

### Steps:
1. On Render Dashboard, click **New +** → **Web Service**.
2. Connect your repository.
3. Set **Runtime** to **Docker**.
4. Render will read `Dockerfile` and `.dockerignore`, build the container, and launch Uvicorn on `$PORT`.

---

## Verifying Your Live Render Deployment

Once Render finishes deploying (status turns to 🟢 **Live**):

1. **Health Check:** Open `https://<your-app>.onrender.com/api/health` -> should return `{"status": "ok"}`.
2. **Interactive API Docs:** Open `https://<your-app>.onrender.com/docs` -> interactive OpenAPI Swagger UI.
3. **Web Application:** Open `https://<your-app>.onrender.com/` -> live ResQAI React Dashboard.
4. **Try Simulation Mode:** Log in or register a new user, click "Simulate Serious Accident", and verify severity prediction, SHAP explanation summary, nearby hospital cards, and emergency response countdown!

---

## Troubleshooting & Tips

- **First Deploy Delay:** Render free tier spins down web services after 15 minutes of inactivity. The first request after sleep may take ~30 seconds to cold start.
- **Model Files:** The build command trains the ML model and saves `model.pkl` into `backend/ml/`. Ensure `python backend/ml/train_model.py` is included in your build command if not using `render.yaml`.
- **Database Persistence:** On Render free web services, disk state resets on redeploy. SQLite database reset on redeploy is expected; for persistent database across redeploys, attach a free Render PostgreSQL database and set `DATABASE_URL` to your Render Postgres connection string.

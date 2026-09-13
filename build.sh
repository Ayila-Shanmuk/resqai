#!/usr/bin/env bash
# Build script for Render deployment
set -e

echo "=== [1/4] Installing Python Backend Dependencies ==="
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "=== [2/4] Training Machine Learning Severity Model ==="
python backend/ml/train_model.py

echo "=== [3/4] Installing Node.js Frontend Dependencies ==="
cd frontend
npm install

echo "=== [4/4] Building React Static Bundle ==="
npm run build

echo "=== ResQAI Production Build Complete! ==="

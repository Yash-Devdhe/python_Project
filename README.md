# Fake News Detection Platform (FastAPI + React)

This project provides a baseline AI/ML system for fake news detection with an attractive web UI.

- Backend: FastAPI with TF‑IDF + LogisticRegression baseline, simple token highlights, feedback logging
- Frontend: React + Vite UI with verdict chip, confidence bar, and top token cues

## Quick Start (no Docker)

1) Install backend deps (uses user site packages):

```bash
python3 -m pip install -r backend/requirements.txt --break-system-packages
```

2) Start the API:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

3) Install frontend deps and run dev server:

```bash
cd frontend
npm ci
npm run dev -- --host 0.0.0.0
```

4) Open the app at:

- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs

Note: The first classify call bootstraps a tiny demo model from `backend/app/data/fake_news_samples.csv` and persists artifacts in `backend/app/ml/artifacts/`.

## Endpoints
- POST /classify: { text } -> label, confidence, highlights, reasons, latency
- POST /feedback: { sample_id, user_label, notes?, text? }
- GET /health

## Environment
- Frontend uses `VITE_API_URL` (defaults to `http://localhost:8000`).

## Docker (if available)
Docker is optional; if installed, you can run:

```bash
docker compose up -d --build
```

This will start the backend on 8000 and frontend on 5173.

# Vigilix

Real-time intelligent video analytics platform for object detection, multi-object tracking, and surveillance event analysis.

## Features

- YOLO-based person and vehicle detection
- ByteTrack multi-object tracking with persistent IDs
- Restricted-zone intrusion detection
- Directional line-crossing events
- People counting and occupancy estimates
- Loitering detection
- Annotated video output with tracks and analytics overlays
- FastAPI upload, analysis, status, and result APIs
- React + TypeScript monitoring dashboard
- Dockerized backend and frontend
- GitHub Actions CI

## Stack

**Computer Vision:** Python, OpenCV, Ultralytics YOLO, ByteTrack  
**Backend:** FastAPI, Pydantic  
**Frontend:** React, TypeScript, Vite  
**Infrastructure:** Docker, Docker Compose, Nginx, GitHub Actions

## Architecture

```text
Video
  ↓
OpenCV frame ingestion
  ↓
YOLO object detection
  ↓
ByteTrack tracking
  ↓
Analytics rules engine
  ├── intrusion
  ├── line crossing
  ├── people counting
  └── loitering
  ↓
FastAPI
  ↓
React dashboard
```

## Local development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. Interactive API documentation is available at `/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and proxies API requests to the local backend.

## Docker

Run the full stack with:

```bash
docker compose up --build
```

Frontend: `http://localhost:8080`  
Backend: `http://localhost:8000`

## Public deployment

The repository includes deployment configuration for a split deployment:

- **Frontend:** Vercel
- **Backend:** Render-compatible Docker service

For the frontend, set:

```text
VITE_API_BASE_URL=https://<your-backend-domain>
```

For the backend, set:

```text
VIGILIX_ENVIRONMENT=production
VIGILIX_CORS_ORIGINS=["https://<your-frontend-domain>"]
```

The first backend startup may need to download the lightweight YOLO model. CPU inference is intended for short demo clips; longer videos are better suited to local or GPU-backed execution.

## API workflow

1. `POST /api/videos` — upload a video
2. `POST /api/videos/{video_id}/analyze` — start analysis
3. `GET /api/videos/{video_id}` — read processing status
4. `GET /api/videos/{video_id}/result` — retrieve metrics, events, and annotated-video URL

## Testing

Backend:

```bash
cd backend
pytest -q
```

Frontend:

```bash
cd frontend
npm run build
```

CI runs both checks on pushes and pull requests.

## Current scope

Vigilix currently focuses on an end-to-end object-detection and tracking workflow for short surveillance videos. Persistent database storage, Redis-backed job processing, classifier/ViT experiments, and ONNX benchmarking are planned as later milestones.

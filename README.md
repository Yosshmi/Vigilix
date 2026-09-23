# Vigilix

End-to-end video analytics application for object detection, multi-object tracking, and surveillance event analysis.

[Live Demo](https://vigilix-xi.vercel.app/) · [API Health](https://vigilix-api.onrender.com/health) · [Interactive API Docs](https://vigilix-api.onrender.com/docs)

## Features

- YOLO-based person and vehicle detection
- ByteTrack multi-object tracking with persistent IDs
- Restricted-zone intrusion detection
- Directional line-crossing events
- People counting and occupancy estimates
- Loitering detection
- Browser-compatible annotated video output with tracks and analytics overlays
- FastAPI upload, analysis, status, and result APIs
- React + TypeScript monitoring dashboard
- Dockerized backend and frontend
- GitHub Actions CI

## Stack

**Computer Vision:** Python, OpenCV, Ultralytics YOLO, ByteTrack  
**Backend:** FastAPI, Pydantic  
**Frontend:** React, TypeScript, Vite  
**Infrastructure:** Docker, Docker Compose, FFmpeg, Nginx, GitHub Actions, Vercel, Render

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

FFmpeg (including `ffprobe`) must also be installed on the host; the Docker image installs it automatically. The API runs at `http://localhost:8000`. Interactive API documentation is available at `/docs`.

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

- **Frontend:** [Vercel](https://vigilix-xi.vercel.app/)
- **Backend:** [Render](https://vigilix-api.onrender.com/health)

For the frontend, set:

```text
VITE_API_BASE_URL=https://vigilix-api.onrender.com
```

For the backend, set:

```text
VIGILIX_ENVIRONMENT=production
VIGILIX_CORS_ORIGINS=["https://vigilix-xi.vercel.app"]
```

The deployed service uses Render's free CPU tier. It can take about a minute to wake after inactivity, and inference is deliberately limited to short demo clips (maximum upload size: 50 MB). Uploaded media and results use ephemeral storage and may be cleared when the service restarts. The first backend startup may also download the lightweight YOLO model.

## API workflow

1. `POST /api/videos` — upload a video
2. `POST /api/videos/{video_id}/analyze` — start analysis
3. `GET /api/videos/{video_id}` — read processing status
4. `GET /api/videos/{video_id}/result` — retrieve metrics, events, and annotated-video URL

## Testing

Backend:

```bash
cd backend
python -m pytest -q
```

Frontend:

```bash
cd frontend
npm run build
```

CI runs both checks on pushes and pull requests. The backend suite includes API, analytics-rule, tracking-state, configuration, and H.264 output compatibility coverage.

## Current scope

Vigilix currently focuses on an end-to-end object-detection and tracking workflow for short surveillance videos. Persistent database storage, Redis-backed job processing, classifier/ViT experiments, and ONNX benchmarking are planned as later milestones.

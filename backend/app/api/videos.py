from dataclasses import asdict
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.schemas.video import AnalysisResponse, VideoStatusResponse, VideoUploadResponse
from app.services.video_analysis import VideoAnalysisService
from app.services.video_store import video_store

router = APIRouter(prefix="/api/videos", tags=["videos"])


def _run_analysis(video_id: str) -> None:
    record = video_store.get(video_id)
    if record is None:
        return

    record.status = "processing"
    record.progress = 0.1

    try:
        service = VideoAnalysisService()
        result = service.analyze(record.input_path, record.output_path)
        record.result = asdict(result)
        record.status = "completed"
        record.progress = 1.0
    except Exception as exc:
        record.status = "failed"
        record.error = str(exc)
        record.progress = 1.0


@router.post("", response_model=VideoUploadResponse)
async def upload_video(file: UploadFile = File(...)) -> VideoUploadResponse:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".mp4", ".mov", ".avi", ".mkv"}:
        raise HTTPException(status_code=400, detail="Unsupported video format")

    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Video is empty")

    max_bytes = 50 * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail="Video exceeds 50 MB limit")

    record = video_store.create(file.filename or "video.mp4")
    record.input_path.write_bytes(content)

    return VideoUploadResponse(
        video_id=record.video_id,
        filename=record.filename,
        status=record.status,
    )


@router.post("/{video_id}/analyze")
def analyze_video(video_id: str, background_tasks: BackgroundTasks) -> dict[str, str]:
    record, scheduled = video_store.queue_for_analysis(video_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Video not found")

    if scheduled:
        background_tasks.add_task(_run_analysis, video_id)
    return {"video_id": video_id, "status": record.status}


@router.get("/{video_id}", response_model=VideoStatusResponse)
def video_status(video_id: str) -> VideoStatusResponse:
    record = video_store.get(video_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Video not found")

    return VideoStatusResponse(
        video_id=record.video_id,
        status=record.status,
        filename=record.filename,
        error=record.error,
        progress=record.progress,
    )


@router.get("/{video_id}/result", response_model=AnalysisResponse)
def video_result(video_id: str) -> AnalysisResponse:
    record = video_store.get(video_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Video not found")

    if record.status != "completed" or record.result is None:
        raise HTTPException(status_code=409, detail="Analysis is not complete")

    result = record.result
    return AnalysisResponse(
        video_id=video_id,
        status="completed",
        frame_count=int(result["frame_count"]),
        processing_seconds=float(result["processing_seconds"]),
        average_fps=float(result["average_fps"]),
        output_url=f"/outputs/{record.output_path.name}",
        events=list(result["events"]),
        analytics=dict(result["analytics"]),
    )

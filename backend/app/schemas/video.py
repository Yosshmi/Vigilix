from pydantic import BaseModel, Field


class VideoUploadResponse(BaseModel):
    video_id: str
    filename: str
    status: str


class AnalysisResponse(BaseModel):
    video_id: str
    status: str
    frame_count: int
    processing_seconds: float
    average_fps: float
    output_url: str
    events: list[dict[str, object]]
    analytics: dict[str, int | float]


class VideoStatusResponse(BaseModel):
    video_id: str
    status: str
    filename: str
    error: str | None = None
    progress: float = Field(default=0.0, ge=0.0, le=1.0)

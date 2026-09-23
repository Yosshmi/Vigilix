from pathlib import Path

from fastapi.testclient import TestClient
from fastapi import BackgroundTasks

from app.api.videos import analyze_video

from app.main import app
from app.services.video_store import video_store


client = TestClient(app)


def test_empty_upload_is_rejected():
    response = client.post("/api/videos", files={"file": ("empty.mp4", b"", "video/mp4")})
    assert response.status_code == 400


def test_queued_analysis_is_not_scheduled_twice():
    record = video_store.create("queued.mp4")
    record.status = "queued"
    tasks = BackgroundTasks()
    try:
        assert analyze_video(record.video_id, tasks)["status"] == "queued"
        assert len(tasks.tasks) == 0
    finally:
        video_store.records.pop(record.video_id)


def test_rejects_unsupported_video_format() -> None:
    response = client.post(
        "/api/videos",
        files={"file": ("notes.txt", b"not a video", "text/plain")},
    )

    assert response.status_code == 400


def test_video_status_404_for_unknown_id() -> None:
    response = client.get("/api/videos/does-not-exist")
    assert response.status_code == 404


def test_upload_registers_video(tmp_path: Path) -> None:
    old_upload_dir = video_store.upload_dir
    old_output_dir = video_store.output_dir

    try:
        video_store.upload_dir = tmp_path / "uploads"
        video_store.output_dir = tmp_path / "outputs"
        video_store.upload_dir.mkdir(parents=True, exist_ok=True)
        video_store.output_dir.mkdir(parents=True, exist_ok=True)

        response = client.post(
            "/api/videos",
            files={"file": ("clip.mp4", b"small-video-placeholder", "video/mp4")},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "uploaded"
        assert body["filename"] == "clip.mp4"
        assert video_store.get(body["video_id"]) is not None
    finally:
        video_store.upload_dir = old_upload_dir
        video_store.output_dir = old_output_dir

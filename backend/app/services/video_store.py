from dataclasses import dataclass, field
from _thread import LockType
from pathlib import Path
from threading import Lock
from uuid import uuid4


@dataclass(slots=True)
class VideoRecord:
    video_id: str
    filename: str
    input_path: Path
    output_path: Path
    status: str = "uploaded"
    error: str | None = None
    progress: float = 0.0
    result: dict[str, object] | None = None


@dataclass
class InMemoryVideoStore:
    upload_dir: Path = field(default_factory=lambda: Path("uploads"))
    output_dir: Path = field(default_factory=lambda: Path("outputs"))
    records: dict[str, VideoRecord] = field(default_factory=dict)
    _state_lock: LockType = field(default_factory=Lock, repr=False)

    def __post_init__(self) -> None:
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create(self, filename: str) -> VideoRecord:
        video_id = str(uuid4())
        safe_name = Path(filename).name
        input_path = self.upload_dir / f"{video_id}-{safe_name}"
        output_path = self.output_dir / f"{video_id}-annotated.mp4"

        record = VideoRecord(
            video_id=video_id,
            filename=safe_name,
            input_path=input_path,
            output_path=output_path,
        )
        self.records[video_id] = record
        return record

    def get(self, video_id: str) -> VideoRecord | None:
        return self.records.get(video_id)

    def queue_for_analysis(self, video_id: str) -> tuple[VideoRecord | None, bool]:
        with self._state_lock:
            record = self.records.get(video_id)
            if record is None:
                return None, False
            if record.status in {"queued", "processing", "completed"}:
                return record, False
            record.status = "queued"
            return record, True


video_store = InMemoryVideoStore()

from dataclasses import asdict, dataclass, field
from uuid import uuid4


@dataclass(slots=True)
class AnalyticsEvent:
    event_type: str
    timestamp_seconds: float
    track_id: int
    object_class: str
    confidence: float
    metadata: dict[str, str | float | int] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))

    def as_dict(self) -> dict[str, object]:
        return asdict(self)

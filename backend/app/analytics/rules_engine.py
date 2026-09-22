from dataclasses import dataclass

from app.analytics.events import AnalyticsEvent
from app.analytics.intrusion import IntrusionRule
from app.analytics.loitering import LoiteringRule
from app.analytics.people_counter import PeopleCounter
from app.vision.tracker import Track


@dataclass(slots=True)
class AnalyticsSnapshot:
    entries: int
    exits: int
    occupancy: int
    active_tracks: int


class AnalyticsEngine:
    def __init__(
        self,
        intrusion_rule: IntrusionRule | None = None,
        people_counter: PeopleCounter | None = None,
        loitering_rule: LoiteringRule | None = None,
    ) -> None:
        self.intrusion_rule = intrusion_rule
        self.people_counter = people_counter
        self.loitering_rule = loitering_rule

    def process_track(self, track: Track, timestamp_seconds: float) -> list[AnalyticsEvent]:
        events: list[AnalyticsEvent] = []

        if self.intrusion_rule and self.intrusion_rule.update(track.track_id, track.center):
            events.append(
                AnalyticsEvent(
                    event_type="restricted_zone_intrusion",
                    timestamp_seconds=timestamp_seconds,
                    track_id=track.track_id,
                    object_class=track.class_name,
                    confidence=track.confidence,
                    metadata={"zone": self.intrusion_rule.zone_id},
                )
            )

        if self.people_counter and track.class_name == "person":
            direction = self.people_counter.update(track.track_id, track.center)
            if direction:
                events.append(
                    AnalyticsEvent(
                        event_type="line_crossing",
                        timestamp_seconds=timestamp_seconds,
                        track_id=track.track_id,
                        object_class=track.class_name,
                        confidence=track.confidence,
                        metadata={"direction": direction},
                    )
                )

        if (
            self.loitering_rule
            and track.class_name == "person"
            and self.loitering_rule.update(track.track_id, track.center, timestamp_seconds)
        ):
            events.append(
                AnalyticsEvent(
                    event_type="loitering",
                    timestamp_seconds=timestamp_seconds,
                    track_id=track.track_id,
                    object_class=track.class_name,
                    confidence=track.confidence,
                    metadata={"zone": self.loitering_rule.zone_id},
                )
            )

        return events

    def snapshot(self, active_tracks: int) -> AnalyticsSnapshot:
        if self.people_counter:
            counts = self.people_counter.snapshot()
            return AnalyticsSnapshot(
                entries=counts.entries,
                exits=counts.exits,
                occupancy=counts.occupancy,
                active_tracks=active_tracks,
            )

        return AnalyticsSnapshot(entries=0, exits=0, occupancy=0, active_tracks=active_tracks)

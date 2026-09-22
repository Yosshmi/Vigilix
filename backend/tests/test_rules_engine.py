from app.analytics.intrusion import IntrusionRule
from app.analytics.loitering import LoiteringRule
from app.analytics.people_counter import PeopleCounter
from app.analytics.rules_engine import AnalyticsEngine
from app.vision.tracker import Track


def make_person(track_id: int, center_x: float, center_y: float, timestamp: float) -> Track:
    return Track(
        track_id=track_id,
        class_id=0,
        class_name="person",
        confidence=0.9,
        bbox=(center_x - 1, center_y - 1, center_x + 1, center_y + 1),
        first_seen=timestamp,
        last_seen=timestamp,
        history=[(center_x, center_y)],
    )


def test_rules_engine_emits_intrusion_event() -> None:
    engine = AnalyticsEngine(
        intrusion_rule=IntrusionRule(
            "restricted",
            [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)],
        )
    )

    events = engine.process_track(make_person(1, 5.0, 5.0, 1.0), 1.0)

    assert len(events) == 1
    assert events[0].event_type == "restricted_zone_intrusion"


def test_rules_engine_emits_loitering_after_threshold() -> None:
    engine = AnalyticsEngine(
        loitering_rule=LoiteringRule(
            "zone",
            [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)],
            threshold_seconds=2.0,
        )
    )

    assert engine.process_track(make_person(2, 5.0, 5.0, 0.0), 0.0) == []
    events = engine.process_track(make_person(2, 5.0, 5.0, 3.0), 3.0)

    assert len(events) == 1
    assert events[0].event_type == "loitering"


def test_people_counter_updates_snapshot() -> None:
    counter = PeopleCounter("door", (0.0, 0.0), (10.0, 0.0))
    engine = AnalyticsEngine(people_counter=counter)

    engine.process_track(make_person(3, 5.0, -2.0, 0.0), 0.0)
    events = engine.process_track(make_person(3, 5.0, 2.0, 1.0), 1.0)

    assert events[0].event_type == "line_crossing"
    assert engine.snapshot(active_tracks=1).entries == 1

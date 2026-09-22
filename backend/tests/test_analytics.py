from app.analytics.intrusion import IntrusionRule
from app.analytics.line_crossing import LineCrossingRule
from app.vision.geometry import point_in_polygon


def test_point_in_polygon() -> None:
    square = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    assert point_in_polygon((5.0, 5.0), square)
    assert not point_in_polygon((15.0, 5.0), square)


def test_intrusion_only_fires_on_entry() -> None:
    rule = IntrusionRule(
        zone_id="restricted",
        polygon=[(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)],
    )

    assert rule.update(1, (5.0, 5.0))
    assert not rule.update(1, (6.0, 6.0))
    assert not rule.update(1, (20.0, 20.0))
    assert rule.update(1, (5.0, 5.0))


def test_line_crossing_reports_direction() -> None:
    rule = LineCrossingRule(
        line_id="entrance",
        start=(0.0, 0.0),
        end=(10.0, 0.0),
    )

    assert rule.update(9, (5.0, -2.0)) is None
    assert rule.update(9, (5.0, 2.0)) == "IN"
    assert rule.update(9, (5.0, -2.0)) == "OUT"

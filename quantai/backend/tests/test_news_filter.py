# backend/tests/test_news_filter.py
from __future__ import annotations

from datetime import UTC, datetime

from app.services.news_filter import NewsFilter


def test_upcoming_events_shape() -> None:
    nf = NewsFilter()
    events = nf.get_upcoming_events(within_hours=72)
    assert isinstance(events, list)


def test_minutes_to_next_event_type() -> None:
    nf = NewsFilter()
    out = nf.minutes_to_next_event(datetime.now(UTC))
    assert out is None or isinstance(out, int)

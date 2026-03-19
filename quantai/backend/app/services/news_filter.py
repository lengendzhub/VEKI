# backend/app/services/news_filter.py
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.config import get_settings


class NewsFilter:
    MOCK_EVENTS = [
        ("NFP", 4, 12, 30, ["USD"]),
        ("CPI", 1, 12, 30, ["USD"]),
        ("FOMC", 2, 18, 0, ["USD"]),
        ("ECB", 3, 11, 45, ["EUR"]),
        ("BOE", 3, 11, 0, ["GBP"]),
        ("GDP", 2, 12, 30, ["USD"]),
    ]

    def __init__(self) -> None:
        self.settings = get_settings()

    def get_upcoming_events(self, within_hours: int = 24) -> list[dict]:
        now = datetime.now(UTC)
        end = now + timedelta(hours=within_hours)
        events: list[dict] = []
        for day_offset in range(0, 8):
            candidate_day = now + timedelta(days=day_offset)
            for name, weekday, hour, minute, currencies in self.MOCK_EVENTS:
                if candidate_day.weekday() != weekday:
                    continue
                dt = datetime(candidate_day.year, candidate_day.month, candidate_day.day, hour, minute, tzinfo=UTC)
                if now <= dt <= end:
                    events.append({"name": name, "datetime": dt.isoformat(), "currencies": currencies})
        events.sort(key=lambda x: x["datetime"])
        return events

    def is_high_impact_window(self, current_time: datetime) -> tuple[bool, str | None]:
        now = current_time.astimezone(UTC)
        events = self.get_upcoming_events(within_hours=48)
        before = timedelta(minutes=self.settings.NEWS_BLOCK_MINUTES_BEFORE)
        after = timedelta(minutes=self.settings.NEWS_BLOCK_MINUTES_AFTER)

        for event in events:
            evt = datetime.fromisoformat(event["datetime"]) if isinstance(event["datetime"], str) else event["datetime"]
            if evt - before <= now <= evt + after:
                return True, str(event["name"])
        return False, None

    def minutes_to_next_event(self, current_time: datetime) -> int | None:
        now = current_time.astimezone(UTC)
        events = self.get_upcoming_events(within_hours=4)
        if not events:
            return None
        evt = datetime.fromisoformat(events[0]["datetime"])
        delta = evt - now
        return max(0, int(delta.total_seconds() // 60))


news_filter = NewsFilter()

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.services.retrain_scheduler import RetrainScheduler


class _FakeScheduler:
    def __init__(self) -> None:
        self.running = False
        self.jobs: list[dict] = []
        self.shutdown_called = False

    def add_job(self, func, trigger, **kwargs) -> None:
        self.jobs.append({"func": func, "trigger": trigger, "kwargs": kwargs})

    def start(self) -> None:
        self.running = True

    def shutdown(self, wait: bool = False) -> None:
        self.shutdown_called = True
        self.running = False


@pytest.mark.asyncio
async def test_start_registers_duka_jobs_when_enabled() -> None:
    scheduler = RetrainScheduler()
    fake = _FakeScheduler()
    scheduler.scheduler = fake  # type: ignore[assignment]

    scheduler.settings.DUKASCOPY_INGEST_ENABLED = True
    scheduler.settings.DUKASCOPY_INGEST_RUN_ON_STARTUP = True

    scheduler.start()

    ids = [job["kwargs"].get("id") for job in fake.jobs]
    assert "daily_summary" in ids
    assert "dukascopy_ingest" in ids
    assert "dukascopy_ingest_startup" in ids


@pytest.mark.asyncio
async def test_ingest_job_runs_symbol_pipeline(monkeypatch: pytest.MonkeyPatch) -> None:
    scheduler = RetrainScheduler()

    scheduler.settings.DUKASCOPY_SYMBOLS = ["EURUSD", "GBPUSD"]
    scheduler.settings.DUKASCOPY_START_DATE = "2025-01-01"
    scheduler.settings.DUKASCOPY_INGEST_LAG_MINUTES = 0
    scheduler.settings.DUKASCOPY_INGEST_PARALLEL_SYMBOLS = 2

    calls: list[tuple[str, datetime, datetime]] = []

    class _FakeSession:
        async def __aenter__(self):
            return object()

        async def __aexit__(self, exc_type, exc, tb) -> None:
            return None

    class _FakeCollector:
        def __init__(self, _session) -> None:
            self._session = _session

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:
            return None

        async def max_cached_timestamp(self, symbol: str, timeframe: str):
            assert timeframe == "5m"
            if symbol == "GBPUSD":
                return datetime.now(UTC)
            return datetime(2025, 1, 2, tzinfo=UTC)

        async def run_pipeline(self, symbol: str, start: datetime, end: datetime) -> None:
            calls.append((symbol, start, end))

    monkeypatch.setattr("app.services.retrain_scheduler.AsyncSessionFactory", lambda: _FakeSession())
    monkeypatch.setattr("app.services.retrain_scheduler.DukascopyCollector", _FakeCollector)

    await scheduler._dukascopy_ingest_job()

    assert len(calls) == 1
    assert calls[0][0] == "EURUSD"
    assert calls[0][1] >= datetime(2025, 1, 2, 0, 5, tzinfo=UTC)


def test_shutdown_stops_running_scheduler() -> None:
    scheduler = RetrainScheduler()
    fake = _FakeScheduler()
    fake.running = True
    scheduler.scheduler = fake  # type: ignore[assignment]

    scheduler.shutdown()

    assert fake.shutdown_called

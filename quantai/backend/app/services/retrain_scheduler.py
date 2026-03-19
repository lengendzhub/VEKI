# backend/app/services/retrain_scheduler.py
from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import get_settings
from app.database import AsyncSessionFactory
from app.ml.train_pipeline import TrainingPipeline
from app.services.dukascopy_collector import DukascopyCollector
from app.services.logger import quant_logger


class RetrainScheduler:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.scheduler = AsyncIOScheduler(timezone="UTC")

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.add_job(
                self._daily_summary,
                "cron",
                hour=22,
                minute=0,
                id="daily_summary",
                replace_existing=True,
            )

            if self.settings.RETRAIN_ENABLED:
                self.scheduler.add_job(
                    self._retrain_job,
                    "cron",
                    hour=self.settings.RETRAIN_CRON_HOUR,
                    minute=self.settings.RETRAIN_CRON_MINUTE,
                    id="retrain_models",
                    replace_existing=True,
                )

            if self.settings.DUKASCOPY_INGEST_ENABLED:
                self.scheduler.add_job(
                    self._dukascopy_ingest_job,
                    "cron",
                    hour=self.settings.DUKASCOPY_INGEST_CRON_HOUR,
                    minute=self.settings.DUKASCOPY_INGEST_CRON_MINUTE,
                    id="dukascopy_ingest",
                    replace_existing=True,
                )

                if self.settings.DUKASCOPY_INGEST_RUN_ON_STARTUP:
                    self.scheduler.add_job(
                        self._dukascopy_ingest_job,
                        "date",
                        run_date=datetime.now(UTC) + timedelta(seconds=10),
                        id="dukascopy_ingest_startup",
                        replace_existing=True,
                    )

            self.scheduler.start()

    async def _daily_summary(self) -> None:
        quant_logger.retrain_started(version="auto", trigger_reason="daily_schedule")

    async def _retrain_job(self) -> None:
        version = datetime.now(UTC).strftime("%Y%m%d%H%M")
        quant_logger.retrain_started(version=version, trigger_reason="scheduled_job")

        try:
            async with AsyncSessionFactory() as session:
                pipeline = TrainingPipeline(db=session)
                meta = await pipeline.run(
                    version=version,
                    symbols=self.settings.DUKASCOPY_SYMBOLS,
                    timeframe=self.settings.RETRAIN_TIMEFRAME,
                    lookback_days=self.settings.RETRAIN_LOOKBACK_DAYS,
                    min_rows=self.settings.RETRAIN_MIN_ROWS,
                )
            quant_logger.retrain_completed(version=version, metrics=meta.get("metrics", {}))
        except Exception as exc:
            quant_logger.error(
                module="retrain_scheduler",
                error_type=type(exc).__name__,
                message=f"retrain failed: {exc}",
                traceback_str="",
            )

    async def _dukascopy_ingest_job(self) -> None:
        configured_start = self._parse_utc(self.settings.DUKASCOPY_START_DATE)
        end = datetime.now(UTC) - timedelta(minutes=max(1, self.settings.DUKASCOPY_INGEST_LAG_MINUTES))
        if configured_start >= end:
            return

        semaphore = asyncio.Semaphore(max(1, self.settings.DUKASCOPY_INGEST_PARALLEL_SYMBOLS))

        async def _run_symbol(symbol: str) -> None:
            async with semaphore:
                try:
                    async with AsyncSessionFactory() as session:
                        async with DukascopyCollector(session) as collector:
                            latest_5m = await collector.max_cached_timestamp(symbol=symbol, timeframe="5m")
                            effective_start = configured_start
                            if latest_5m is not None:
                                candidate = latest_5m + timedelta(minutes=5)
                                if candidate > effective_start:
                                    effective_start = candidate

                            if effective_start >= end:
                                return

                            await collector.run_pipeline(symbol=symbol, start=effective_start, end=end)
                except Exception as exc:
                    quant_logger.error(
                        module="retrain_scheduler",
                        error_type=type(exc).__name__,
                        message=f"dukascopy ingest failed for {symbol}: {exc}",
                        traceback_str="",
                    )

        await asyncio.gather(*(_run_symbol(symbol) for symbol in self.settings.DUKASCOPY_SYMBOLS))

    def _parse_utc(self, value: str) -> datetime:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

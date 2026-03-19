# backend/scripts/download_data.py
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import get_settings
from app.database import AsyncSessionFactory, init_db
from app.services.dukascopy_collector import DukascopyCollector

logger = logging.getLogger("dukascopy_download")


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download and store Dukascopy historical data")
    parser.add_argument("--symbols", nargs="*", help="Optional symbol override list")
    parser.add_argument("--start", type=str, help="Start date in ISO format (UTC)")
    parser.add_argument("--end", type=str, help="End date in ISO format (UTC)")
    parser.add_argument("--parallel", type=int, default=2, help="Parallel symbols")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


async def run_symbol_pipeline(symbol: str, start: datetime, end: datetime) -> None:
    async with AsyncSessionFactory() as session:
        async with DukascopyCollector(session) as collector:
            latest_5m = await collector.max_cached_timestamp(symbol=symbol, timeframe="5m")
            effective_start = start
            if latest_5m is not None:
                candidate = latest_5m + timedelta(minutes=5)
                if candidate > effective_start:
                    effective_start = candidate
                    logger.info("resume.from_db | symbol=%s | start=%s", symbol, effective_start.isoformat())

            if effective_start >= end:
                logger.info("skip.symbol.up_to_date | symbol=%s", symbol)
                return

            await collector.run_pipeline(symbol=symbol, start=effective_start, end=end)


async def main_async() -> None:
    args = parse_args()
    configure_logging(args.verbose)
    settings = get_settings()

    symbols = args.symbols if args.symbols else settings.DUKASCOPY_SYMBOLS
    start = parse_datetime(args.start) if args.start else parse_datetime(settings.DUKASCOPY_START_DATE)
    end = parse_datetime(args.end) if args.end else parse_datetime(settings.DUKASCOPY_END_DATE)

    if end <= start:
        raise ValueError("end must be greater than start")

    logger.info("pipeline.init | symbols=%s | start=%s | end=%s", symbols, start.isoformat(), end.isoformat())

    await init_db()

    semaphore = asyncio.Semaphore(max(1, args.parallel))

    async def wrapped(symbol: str) -> None:
        async with semaphore:
            try:
                logger.info("pipeline.symbol.start | %s", symbol)
                await run_symbol_pipeline(symbol=symbol, start=start, end=end)
                logger.info("pipeline.symbol.done | %s", symbol)
            except Exception as exc:
                logger.exception("pipeline.symbol.failed | %s | %s", symbol, exc)

    await asyncio.gather(*(wrapped(sym) for sym in symbols))
    logger.info("pipeline.completed")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()

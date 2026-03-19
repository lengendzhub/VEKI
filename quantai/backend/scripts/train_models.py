from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import get_settings
from app.database import AsyncSessionFactory, init_db
from app.ml.train_pipeline import TrainingPipeline

logger = logging.getLogger("model_training")


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train QuantAI models from OHLCV cache")
    parser.add_argument("--symbols", nargs="*", help="Symbol override list")
    parser.add_argument("--timeframe", type=str, help="Training timeframe override, e.g. 5M")
    parser.add_argument("--lookback-days", type=int, help="Lookback days override")
    parser.add_argument("--min-rows", type=int, help="Minimum required rows")
    parser.add_argument("--version", type=str, help="Optional model version")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logs")
    return parser.parse_args()


async def main_async() -> None:
    args = parse_args()
    configure_logging(args.verbose)

    settings = get_settings()
    symbols = args.symbols if args.symbols else settings.DUKASCOPY_SYMBOLS
    timeframe = args.timeframe if args.timeframe else settings.RETRAIN_TIMEFRAME
    lookback_days = args.lookback_days if args.lookback_days else settings.RETRAIN_LOOKBACK_DAYS
    min_rows = args.min_rows if args.min_rows else settings.RETRAIN_MIN_ROWS
    version = args.version if args.version else datetime.now(UTC).strftime("%Y%m%d%H%M")

    await init_db()

    async with AsyncSessionFactory() as session:
        pipeline = TrainingPipeline(db=session)
        out = await pipeline.run(
            version=version,
            symbols=symbols,
            timeframe=timeframe,
            lookback_days=lookback_days,
            min_rows=min_rows,
        )

    logger.info("training.completed | version=%s | rows=%s", version, out.get("rows"))
    logger.info("training.metrics | %s", out.get("metrics"))


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()

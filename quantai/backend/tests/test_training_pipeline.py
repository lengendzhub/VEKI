from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.ml.train_pipeline import TrainingPipeline
from app.models.ohlcv import OhlcvCache


@pytest.mark.asyncio
async def test_training_pipeline_runs_and_returns_metrics() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    start = datetime.now(UTC) - timedelta(days=10)
    rows: list[OhlcvCache] = []
    for i in range(600):
        ts = start + timedelta(minutes=5 * i)
        base = 1.05 + (i * 0.00001)
        rows.append(
            OhlcvCache(
                symbol="EURUSD",
                timeframe="5M",
                timestamp=ts,
                open=base,
                high=base + 0.0004,
                low=base - 0.0003,
                close=base + (0.0001 if i % 2 == 0 else -0.0001),
                volume=1000 + i,
            )
        )

    async with session_factory() as session:
        session.add_all(rows)
        await session.commit()

    async with session_factory() as session:
        pipeline = TrainingPipeline(db=session, models_dir="./models_test")
        out = await pipeline.run(
            version="test_v1",
            symbols=["EURUSD"],
            timeframe="5M",
            lookback_days=365,
            min_rows=200,
        )

    assert out["version"] == "test_v1"
    assert out["rows"] >= 200
    assert "metrics" in out
    assert "meta" in out["metrics"]

    await engine.dispose()

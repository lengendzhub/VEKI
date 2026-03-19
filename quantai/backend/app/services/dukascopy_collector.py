# backend/app/services/dukascopy_collector.py
from __future__ import annotations

import asyncio
import json
import logging
import lzma
import struct
import traceback
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
import pandas as pd
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.ohlcv import OhlcvCache

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DownloadChunk:
    symbol: str
    start: datetime
    end: datetime

    @property
    def key(self) -> str:
        return f"{self.symbol}:{self.start.isoformat()}:{self.end.isoformat()}"


class DukascopyCollector:
    """Production-ready Dukascopy ingestion service with caching and resume support."""

    SUPPORTED_TIMEFRAMES: dict[str, str] = {
        "1m": "1min",
        "5m": "5min",
        "15m": "15min",
        "1h": "1h",
        "4h": "4h",
    }

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.settings = get_settings()
        self.retry_count = 3
        self.chunk_hours = 1
        self.request_timeout_seconds = 30.0
        self.parallel_download_workers = 8

        self.cache_root = Path("./data/dukascopy_cache").resolve()
        self.state_root = Path("./data/dukascopy_state").resolve()
        self.cache_root.mkdir(parents=True, exist_ok=True)
        self.state_root.mkdir(parents=True, exist_ok=True)

        self._semaphore = asyncio.Semaphore(self.parallel_download_workers)
        self._http_client = httpx.AsyncClient(timeout=self.request_timeout_seconds)
        self._dukascopy_module: Any | None = self._try_import_dukascopy()

    async def close(self) -> None:
        await self._http_client.aclose()

    async def __aenter__(self) -> "DukascopyCollector":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        await self.close()

    async def download_ticks(self, symbol: str, start: datetime, end: datetime) -> pd.DataFrame:
        start_utc = self._to_utc(start)
        end_utc = self._to_utc(end)
        if end_utc <= start_utc:
            raise ValueError("end must be greater than start")

        logger.info("dukascopy.download.start", extra={"symbol": symbol, "start": start_utc.isoformat(), "end": end_utc.isoformat()})
        chunks = self._build_hour_chunks(symbol=symbol, start=start_utc, end=end_utc)
        state = self._load_resume_state(symbol=symbol, start=start_utc, end=end_utc)

        data_frames: list[pd.DataFrame] = []
        completed = set(state.get("completed_chunks", []))
        pending = [chunk for chunk in chunks if chunk.key not in completed]

        if not pending and chunks:
            logger.info("dukascopy.download.resume_hit", extra={"symbol": symbol, "chunks": len(chunks)})

        total = len(chunks)
        processed = len(completed)

        for batch_start in range(0, len(pending), self.parallel_download_workers):
            batch = pending[batch_start : batch_start + self.parallel_download_workers]
            results = await asyncio.gather(*(self._download_chunk_with_retry(chunk) for chunk in batch), return_exceptions=True)

            for item in results:
                if isinstance(item, Exception):
                    logger.error(
                        "dukascopy.download.chunk_exception",
                        extra={"symbol": symbol, "error": str(item), "traceback": traceback.format_exc()},
                    )
                    continue

                chunk, frame = item
                completed.add(chunk.key)
                processed += 1
                if not frame.empty:
                    data_frames.append(frame)

                if processed % 24 == 0 or processed == total:
                    logger.info("dukascopy.download.progress", extra={"symbol": symbol, "processed": processed, "total": total})

                self._save_resume_state(
                    symbol=symbol,
                    start=start_utc,
                    end=end_utc,
                    completed_chunks=sorted(completed),
                )

        if data_frames:
            df = pd.concat(data_frames, ignore_index=True)
        else:
            df = pd.DataFrame(columns=["timestamp", "bid", "ask", "price", "volume"])

        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
            df = df.sort_values("timestamp").drop_duplicates(subset=["timestamp"], keep="last").reset_index(drop=True)

        logger.info("dukascopy.download.done", extra={"symbol": symbol, "rows": int(len(df))})
        return df

    async def convert_to_ohlc(self, df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        if timeframe not in self.SUPPORTED_TIMEFRAMES:
            raise ValueError(f"Unsupported timeframe '{timeframe}'. Supported: {list(self.SUPPORTED_TIMEFRAMES)}")

        if df.empty:
            return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

        if "timestamp" not in df.columns:
            raise ValueError("Input DataFrame must include 'timestamp' column")

        work = df.copy()
        work["timestamp"] = pd.to_datetime(work["timestamp"], utc=True)
        work = work.sort_values("timestamp").drop_duplicates(subset=["timestamp"], keep="last")

        if "price" not in work.columns:
            if "close" in work.columns:
                work["price"] = work["close"]
            else:
                raise ValueError("Input DataFrame must include 'price' or 'close' column")

        if "volume" not in work.columns:
            work["volume"] = 0.0

        rule = self.SUPPORTED_TIMEFRAMES[timeframe]
        indexed = work.set_index("timestamp")

        ohlc = indexed["price"].resample(rule).ohlc()
        vol = indexed["volume"].resample(rule).sum()
        out = pd.concat([ohlc, vol], axis=1).rename(columns={"volume": "volume"})

        if out.empty:
            return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

        full_index = pd.date_range(
            start=out.index.min().floor(rule),
            end=out.index.max().floor(rule),
            freq=rule,
            tz=UTC,
        )
        out = out.reindex(full_index)

        out["close"] = out["close"].ffill().bfill()
        out["open"] = out["open"].fillna(out["close"].shift(1)).fillna(out["close"])
        out["high"] = out["high"].fillna(pd.concat([out["open"], out["close"]], axis=1).max(axis=1))
        out["low"] = out["low"].fillna(pd.concat([out["open"], out["close"]], axis=1).min(axis=1))
        out["volume"] = out["volume"].fillna(0.0)

        out = out.reset_index().rename(columns={"index": "timestamp"})
        out = out[["timestamp", "open", "high", "low", "close", "volume"]]
        out = await self.clean_data(out)
        return out

    async def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        work = df.copy()
        if "timestamp" not in work.columns:
            raise ValueError("DataFrame must include 'timestamp' column")

        work["timestamp"] = pd.to_datetime(work["timestamp"], utc=True)
        work = work.sort_values("timestamp").drop_duplicates(subset=["timestamp"], keep="last")

        numeric_cols = [c for c in ["bid", "ask", "price", "open", "high", "low", "close", "volume"] if c in work.columns]
        for col in numeric_cols:
            work[col] = pd.to_numeric(work[col], errors="coerce")

        price_cols = [c for c in ["bid", "ask", "price", "open", "high", "low", "close"] if c in work.columns]
        if price_cols:
            mask_positive = (work[price_cols] > 0).all(axis=1)
            work = work.loc[mask_positive]

        if {"high", "low", "open", "close"}.issubset(work.columns):
            mask_range = (
                (work["high"] >= work["low"])
                & (work["open"] >= work["low"])
                & (work["open"] <= work["high"])
                & (work["close"] >= work["low"])
                & (work["close"] <= work["high"])
            )
            work = work.loc[mask_range]

            pct = work["close"].pct_change().abs()
            spike_mask = pct.fillna(0.0) <= 0.05
            work = work.loc[spike_mask]
        elif "price" in work.columns:
            pct = work["price"].pct_change().abs()
            spike_mask = pct.fillna(0.0) <= 0.05
            work = work.loc[spike_mask]

        work = work.dropna(subset=[c for c in ["timestamp", "open", "high", "low", "close", "price"] if c in work.columns])
        work = work.reset_index(drop=True)
        return work

    async def store_ohlc(self, df: pd.DataFrame, symbol: str, timeframe: str) -> None:
        if df.empty:
            logger.warning("dukascopy.store.empty", extra={"symbol": symbol, "timeframe": timeframe})
            return

        required = {"timestamp", "open", "high", "low", "close", "volume"}
        if not required.issubset(df.columns):
            raise ValueError(f"OHLC DataFrame missing columns: {required - set(df.columns)}")

        records = [
            {
                "id": str(uuid.uuid4()),
                "symbol": symbol,
                "timeframe": timeframe.upper(),
                "timestamp": self._to_utc(pd.Timestamp(row.timestamp).to_pydatetime()),
                "open": float(row.open),
                "high": float(row.high),
                "low": float(row.low),
                "close": float(row.close),
                "volume": float(row.volume),
            }
            for row in df.itertuples(index=False)
        ]

        batch_size = 5000
        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            stmt = pg_insert(OhlcvCache).values(batch).on_conflict_do_nothing(
                index_elements=["symbol", "timeframe", "timestamp"]
            )
            await self.db.execute(stmt)

        await self.db.commit()
        logger.info("dukascopy.store.done", extra={"symbol": symbol, "timeframe": timeframe, "rows": len(records)})

    async def run_pipeline(self, symbol: str, start: datetime, end: datetime) -> None:
        logger.info("dukascopy.pipeline.start", extra={"symbol": symbol, "start": start.isoformat(), "end": end.isoformat()})

        ticks = await self.download_ticks(symbol=symbol, start=start, end=end)
        ticks = await self.clean_data(ticks)

        if ticks.empty:
            logger.warning("dukascopy.pipeline.no_ticks", extra={"symbol": symbol})
            return

        for tf in ["1m", "5m", "15m", "1h", "4h"]:
            ohlc = await self.convert_to_ohlc(ticks, timeframe=tf)
            ohlc = await self.clean_data(ohlc)
            await self.store_ohlc(ohlc, symbol=symbol, timeframe=tf)

        logger.info("dukascopy.pipeline.done", extra={"symbol": symbol})

    async def _download_chunk_with_retry(self, chunk: DownloadChunk) -> tuple[DownloadChunk, pd.DataFrame]:
        cached = await self._read_chunk_cache(chunk)
        if cached is not None:
            return chunk, cached

        last_error: Exception | None = None
        for attempt in range(1, self.retry_count + 1):
            try:
                async with self._semaphore:
                    frame = await self._download_chunk(chunk)
                await self._write_chunk_cache(chunk, frame)
                return chunk, frame
            except Exception as exc:  # pragma: no cover
                last_error = exc
                logger.warning(
                    "dukascopy.download.retry",
                    extra={
                        "symbol": chunk.symbol,
                        "chunk_start": chunk.start.isoformat(),
                        "attempt": attempt,
                        "error": str(exc),
                    },
                )
                await asyncio.sleep(min(5, attempt))

        if last_error is None:
            raise RuntimeError("Unknown download error")
        raise last_error

    async def _download_chunk(self, chunk: DownloadChunk) -> pd.DataFrame:
        library_frame = await self._download_chunk_via_library(chunk)
        if library_frame is not None:
            return library_frame

        return await self._download_chunk_via_http(chunk)

    async def _download_chunk_via_library(self, chunk: DownloadChunk) -> pd.DataFrame | None:
        if self._dukascopy_module is None:
            return None

        module = self._dukascopy_module
        try:
            if hasattr(module, "download_ticks"):
                maybe = module.download_ticks(chunk.symbol, chunk.start, chunk.end)
                frame = await self._resolve_maybe_awaitable(maybe)
                return self._normalize_tick_frame(frame)

            if hasattr(module, "get_ticks"):
                maybe = module.get_ticks(chunk.symbol, chunk.start, chunk.end)
                frame = await self._resolve_maybe_awaitable(maybe)
                return self._normalize_tick_frame(frame)

            if hasattr(module, "Dukascopy"):
                client = module.Dukascopy()
                if hasattr(client, "get_ticks"):
                    frame = await asyncio.to_thread(client.get_ticks, chunk.symbol, chunk.start, chunk.end)
                    return self._normalize_tick_frame(frame)
        except Exception as exc:
            logger.warning(
                "dukascopy.library.failed",
                extra={"symbol": chunk.symbol, "chunk_start": chunk.start.isoformat(), "error": str(exc)},
            )

        return None

    async def _download_chunk_via_http(self, chunk: DownloadChunk) -> pd.DataFrame:
        hour_cursor = chunk.start
        all_rows: list[dict[str, Any]] = []

        while hour_cursor < chunk.end:
            url = self._build_dukascopy_url(symbol=chunk.symbol, hour=hour_cursor)
            response = await self._http_client.get(url)

            if response.status_code == 404:
                hour_cursor += timedelta(hours=1)
                continue

            response.raise_for_status()
            rows = self._decode_bi5(content=response.content, symbol=chunk.symbol, base_hour=hour_cursor)
            all_rows.extend(rows)
            hour_cursor += timedelta(hours=1)

        if not all_rows:
            return pd.DataFrame(columns=["timestamp", "bid", "ask", "price", "volume"])

        df = pd.DataFrame(all_rows)
        return self._normalize_tick_frame(df)

    def _decode_bi5(self, content: bytes, symbol: str, base_hour: datetime) -> list[dict[str, Any]]:
        if not content:
            return []

        try:
            decoded = lzma.decompress(content)
        except lzma.LZMAError as exc:
            logger.warning(
                "dukascopy.decode.corrupted_chunk",
                extra={"symbol": symbol, "base_hour": base_hour.isoformat(), "error": str(exc)},
            )
            return []

        rows: list[dict[str, Any]] = []
        price_divisor = self._price_divisor(symbol)

        for idx in range(0, len(decoded), 20):
            part = decoded[idx : idx + 20]
            if len(part) != 20:
                continue

            try:
                ms, ask_raw, bid_raw, ask_vol, bid_vol = struct.unpack(">iiiff", part)
                ask = ask_raw / price_divisor
                bid = bid_raw / price_divisor
                volume = float(max(0.0, ask_vol) + max(0.0, bid_vol))
            except struct.error:
                ms, ask_raw, bid_raw, ask_vol_i, bid_vol_i = struct.unpack(">iiiii", part)
                ask = ask_raw / price_divisor
                bid = bid_raw / price_divisor
                volume = float(max(0, ask_vol_i) + max(0, bid_vol_i))

            if ask <= 0 or bid <= 0:
                continue

            ts = base_hour + timedelta(milliseconds=int(ms))
            rows.append(
                {
                    "timestamp": ts,
                    "bid": bid,
                    "ask": ask,
                    "price": (ask + bid) / 2,
                    "volume": volume,
                }
            )

        return rows

    def _normalize_tick_frame(self, frame: Any) -> pd.DataFrame:
        if frame is None:
            return pd.DataFrame(columns=["timestamp", "bid", "ask", "price", "volume"])

        df = pd.DataFrame(frame)
        if df.empty:
            return pd.DataFrame(columns=["timestamp", "bid", "ask", "price", "volume"])

        rename_map = {
            "time": "timestamp",
            "datetime": "timestamp",
            "DateTime": "timestamp",
            "askPrice": "ask",
            "bidPrice": "bid",
            "Ask": "ask",
            "Bid": "bid",
            "AskVolume": "ask_volume",
            "BidVolume": "bid_volume",
        }
        df = df.rename(columns=rename_map)

        if "timestamp" not in df.columns:
            raise ValueError("Dukascopy tick frame missing timestamp column")

        if "price" not in df.columns:
            if {"ask", "bid"}.issubset(df.columns):
                df["price"] = (pd.to_numeric(df["ask"], errors="coerce") + pd.to_numeric(df["bid"], errors="coerce")) / 2
            elif "close" in df.columns:
                df["price"] = pd.to_numeric(df["close"], errors="coerce")
            else:
                raise ValueError("Dukascopy tick frame missing ask/bid or price columns")

        if "volume" not in df.columns:
            ask_vol = pd.to_numeric(df.get("ask_volume", 0.0), errors="coerce").fillna(0.0)
            bid_vol = pd.to_numeric(df.get("bid_volume", 0.0), errors="coerce").fillna(0.0)
            df["volume"] = ask_vol + bid_vol

        if "ask" not in df.columns:
            df["ask"] = pd.to_numeric(df["price"], errors="coerce")
        if "bid" not in df.columns:
            df["bid"] = pd.to_numeric(df["price"], errors="coerce")

        df = df[["timestamp", "bid", "ask", "price", "volume"]].copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        for col in ["bid", "ask", "price", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=["timestamp", "price"]).sort_values("timestamp")
        return df.reset_index(drop=True)

    async def _read_chunk_cache(self, chunk: DownloadChunk) -> pd.DataFrame | None:
        path = self._chunk_cache_path(chunk)
        if not path.exists():
            return None
        try:
            return await asyncio.to_thread(pd.read_pickle, path)
        except Exception as exc:
            logger.warning("dukascopy.cache.read_failed", extra={"path": str(path), "error": str(exc)})
            return None

    async def _write_chunk_cache(self, chunk: DownloadChunk, df: pd.DataFrame) -> None:
        path = self._chunk_cache_path(chunk)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            await asyncio.to_thread(df.to_pickle, path)
        except Exception as exc:
            logger.warning("dukascopy.cache.write_failed", extra={"path": str(path), "error": str(exc)})

    def _chunk_cache_path(self, chunk: DownloadChunk) -> Path:
        dt = chunk.start
        return self.cache_root / chunk.symbol / f"{dt.year:04d}" / f"{dt.month:02d}" / f"{dt.day:02d}" / f"{dt.hour:02d}.pkl"

    def _build_hour_chunks(self, symbol: str, start: datetime, end: datetime) -> list[DownloadChunk]:
        chunks: list[DownloadChunk] = []
        cursor = start.replace(minute=0, second=0, microsecond=0)
        while cursor < end:
            next_cursor = min(cursor + timedelta(hours=self.chunk_hours), end)
            chunks.append(DownloadChunk(symbol=symbol, start=cursor, end=next_cursor))
            cursor = next_cursor
        return chunks

    def _build_dukascopy_url(self, symbol: str, hour: datetime) -> str:
        # Dukascopy path uses zero-based month index.
        return (
            "https://datafeed.dukascopy.com/datafeed/"
            f"{symbol}/{hour.year}/{hour.month - 1:02d}/{hour.day:02d}/{hour.hour:02d}h_ticks.bi5"
        )

    def _state_path(self, symbol: str, start: datetime, end: datetime) -> Path:
        key = f"{symbol}_{start.strftime('%Y%m%d%H%M')}_{end.strftime('%Y%m%d%H%M')}"
        return self.state_root / f"{key}.json"

    def _load_resume_state(self, symbol: str, start: datetime, end: datetime) -> dict[str, Any]:
        path = self._state_path(symbol=symbol, start=start, end=end)
        if not path.exists():
            return {"completed_chunks": []}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {"completed_chunks": []}

    def _save_resume_state(self, symbol: str, start: datetime, end: datetime, completed_chunks: list[str]) -> None:
        path = self._state_path(symbol=symbol, start=start, end=end)
        payload = {
            "symbol": symbol,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
            "completed_chunks": completed_chunks,
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _to_utc(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    def _price_divisor(self, symbol: str) -> float:
        upper = symbol.upper()
        if upper.endswith("JPY"):
            return 1000.0
        if upper in {"XAUUSD", "XAGUSD"}:
            return 100.0
        return 100000.0

    def _try_import_dukascopy(self) -> Any | None:
        try:
            import dukascopy  # type: ignore

            logger.info("dukascopy.library.loaded")
            return dukascopy
        except Exception:
            logger.info("dukascopy.library.unavailable_using_http_fallback")
            return None

    async def _resolve_maybe_awaitable(self, maybe: Any) -> Any:
        if asyncio.iscoroutine(maybe):
            return await maybe
        return maybe

    async def max_cached_timestamp(self, symbol: str, timeframe: str) -> datetime | None:
        stmt = (
            select(OhlcvCache.timestamp)
            .where(OhlcvCache.symbol == symbol, OhlcvCache.timeframe == timeframe.upper())
            .order_by(OhlcvCache.timestamp.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        ts = result.scalar_one_or_none()
        if ts is None:
            return None
        if ts.tzinfo is None:
            return ts.replace(tzinfo=UTC)
        return ts.astimezone(UTC)

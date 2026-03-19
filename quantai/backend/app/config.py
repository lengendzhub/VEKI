# backend/app/config.py
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://quantai:quantai@localhost:5432/quantai"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    TOKEN_EXPIRE_MIN: int = 1440

    MT5_LOGIN: int = 0
    MT5_PASSWORD: str = ""
    MT5_SERVER: str = ""

    MAX_RISK_PCT: float = 0.01
    MAX_DAILY_DD: float = 0.05
    CONFIDENCE_GATE: float = 0.80

    MODELS_DIR: str = "./models"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    SYMBOLS: List[str] = Field(default_factory=lambda: ["EURUSD", "GBPUSD", "USDJPY"])
    TIMEFRAMES: List[str] = Field(default_factory=lambda: ["M5", "H1", "H4"])

    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_ALLOWED_CHAT_IDS: List[int] = Field(default_factory=list)
    TELEGRAM_ADMIN_CHAT_ID: int = 0

    NEWS_BLOCK_MINUTES_BEFORE: int = 15
    NEWS_BLOCK_MINUTES_AFTER: int = 15
    MAX_SPREAD_PIPS: float = 2.0
    MAX_SLIPPAGE_PIPS: float = 1.0

    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10

    FCM_SERVER_KEY: str | None = None

    KILL_SWITCH_DD_THRESHOLD: float = 0.045
    MTF_CONFLUENCE_REQUIRED: bool = True
    ENABLE_PARTIAL_TP: bool = True
    ENABLE_TRAILING_STOP: bool = True
    AUDIT_LOG_RETENTION_DAYS: int = 365

    INTERNAL_API_KEY: str = "internal-dev-key"

    DUKASCOPY_SYMBOLS: List[str] = Field(default_factory=lambda: ["EURUSD", "GBPUSD", "XAUUSD"])
    DUKASCOPY_START_DATE: str = "2022-01-01"
    DUKASCOPY_END_DATE: str = "2024-01-01"
    DUKASCOPY_INGEST_ENABLED: bool = True
    DUKASCOPY_INGEST_CRON_HOUR: int = 0
    DUKASCOPY_INGEST_CRON_MINUTE: int = 20
    DUKASCOPY_INGEST_PARALLEL_SYMBOLS: int = 2
    DUKASCOPY_INGEST_LAG_MINUTES: int = 10
    DUKASCOPY_INGEST_RUN_ON_STARTUP: bool = False

    RETRAIN_ENABLED: bool = True
    RETRAIN_CRON_HOUR: int = 1
    RETRAIN_CRON_MINUTE: int = 15
    RETRAIN_LOOKBACK_DAYS: int = 180
    RETRAIN_TIMEFRAME: str = "5M"
    RETRAIN_MIN_ROWS: int = 500


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return singleton settings object."""
    return Settings()

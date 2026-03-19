# backend/app/main.py
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from redis.asyncio import Redis

from app.broker.mt5_broker import MT5Broker
from app.config import get_settings
from app.core.websocket_manager import ConnectionManager
from app.core.rate_limiter import RateLimiter
from app.database import init_db
from app.routers import account, analysis, auth, metrics, strategy, trades, websocket
from app.services.ai_engine import AIEngine
from app.services.backtester import Backtester
from app.services.data_collector import DataCollector
from app.services.data_validator import DataValidator
from app.services.feature_engineer import FeatureEngineer
from app.services.kill_switch import KillSwitch
from app.services.news_filter import news_filter
from app.services.retrain_scheduler import RetrainScheduler
from app.services.training_monitor import training_monitor


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    await init_db()
    redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    ws_manager = ConnectionManager(redis_client)

    async def _training_broadcast(payload: dict) -> None:
        await ws_manager.broadcast(payload)

    training_monitor.set_broadcast_callback(_training_broadcast)

    feature_engineer = FeatureEngineer()
    ai_engine = AIEngine(feature_engineer=feature_engineer, news_filter=news_filter, validator=DataValidator())
    await ai_engine.load_models()
    backtester = Backtester(ai_engine=ai_engine, feature_engineer=feature_engineer)
    broker = MT5Broker(mock_mode=True)
    await broker.connect()

    app.state.redis = redis_client
    app.state.ws_manager = ws_manager
    app.state.rate_limiter = RateLimiter(redis_client)
    app.state.kill_switch = KillSwitch(redis_client)
    app.state.backtester = backtester
    app.state.broker = broker
    app.state.risk_manager = None
    app.state.data_collector = DataCollector()
    app.state.retrain_scheduler = RetrainScheduler()
    app.state.retrain_scheduler.start()

    yield

    app.state.retrain_scheduler.shutdown()
    training_monitor.set_broadcast_callback(None)
    await broker.disconnect()
    await redis_client.close()


app = FastAPI(title="QuantAI", version="3.0", lifespan=lifespan)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    limiter: RateLimiter = request.app.state.rate_limiter
    user_id = request.headers.get("x-user-id")
    await limiter.check(request, user_id=user_id)
    return await call_next(request)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


app.include_router(auth.router, prefix="/api/v1")
app.include_router(account.router, prefix="/api/v1")
app.include_router(trades.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1", dependencies=[Depends(lambda request: request.app.state.backtester)])
app.include_router(strategy.router, prefix="/api/v1")
app.include_router(metrics.router, prefix="/api/v1")
app.include_router(websocket.router)

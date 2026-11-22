from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router
from app.db.session import AsyncSessionLocal
from app.services.paper_market_data import PaperMarketDataProvider
from app.services.automation_engine import AutomationEngine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    paper_provider = PaperMarketDataProvider()
    engine = AutomationEngine(
        session_factory=AsyncSessionLocal,
        paper_market_data=paper_provider,
    )
    app.state.paper_market_data = paper_provider
    app.state.automation_engine = engine

    engine.start()
    yield

    # Shutdown
    await engine.stop()


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="RAGAB AI Trade API — personal automation trading (paper-first).",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health():
    engine: AutomationEngine | None = getattr(app.state, "automation_engine", None)
    return {
        "status": "ok",
        "paper_trading_only": settings.paper_trading_only,
        "automation_running": engine._running if engine else False,
        "active_jobs": len(engine.jobs) if engine else 0,
    }


@app.get("/ready", tags=["system"])
async def ready():
    return {"status": "ready"}


app.include_router(api_router, prefix=settings.api_v1_prefix)

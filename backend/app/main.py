from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router
from app.services.paper_market_data import PaperMarketDataProvider

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="RAGAB AI Trade API — paper-trading foundation.",
)

app.state.paper_market_data = PaperMarketDataProvider()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "paper_trading_only": settings.paper_trading_only}

@app.get("/ready", tags=["system"])
async def ready():
    return {"status": "ready"}

app.include_router(api_router, prefix=settings.api_v1_prefix)

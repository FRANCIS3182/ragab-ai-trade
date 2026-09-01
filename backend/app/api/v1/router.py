from fastapi import APIRouter

from app.api.v1.routes import auth, paper_trading, ai, risk_settings, automation, trading_accounts

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    paper_trading.router,
    prefix="/paper",
    tags=["paper trading"],
)
api_router.include_router(
    ai.router,
    prefix="/ai",
    tags=["AI"],
)
api_router.include_router(
    risk_settings.router,
    prefix="/risk-settings",
    tags=["risk settings"],
)

api_router.include_router(automation.router, prefix="/automation", tags=["automation"])

api_router.include_router(trading_accounts.router, prefix="/trading-accounts", tags=["trading accounts"])

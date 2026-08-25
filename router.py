from fastapi import APIRouter
from app.api.v1.routes import auth, paper_trading

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(paper_trading.router, prefix="/paper", tags=["paper trading"])

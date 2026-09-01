from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.ai.analyzer import analyze_market

router = APIRouter(prefix="/ai", tags=["AI"])


class MarketAnalysisRequest(BaseModel):
    symbol: str = Field(min_length=2, max_length=30)
    timeframe: str = Field(min_length=1, max_length=10)
    price: float = Field(gt=0)
    moving_average: float = Field(gt=0)


@router.post("/analyze")
def ai_analyze(request: MarketAnalysisRequest):
    result = analyze_market(
        symbol=request.symbol,
        timeframe=request.timeframe,
        price=request.price,
        moving_average=request.moving_average,
    )

    return {
        "symbol": result.symbol,
        "timeframe": result.timeframe,
        "signal": result.signal,
        "confidence": result.confidence,
        "reason": result.reason,
        "execution": "paper_only",
    }

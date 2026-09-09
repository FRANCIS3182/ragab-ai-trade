from dataclasses import dataclass
from typing import Literal


Signal = Literal["BUY", "SELL", "HOLD"]


@dataclass
class MarketAnalysis:
    symbol: str
    timeframe: str
    signal: Signal
    confidence: float
    reason: str


def analyze_market(
    symbol: str,
    timeframe: str,
    price: float,
    moving_average: float,
) -> MarketAnalysis:
    if price > moving_average:
        signal: Signal = "BUY"
        confidence = 0.60
        reason = "Price is above the reference moving average."
    elif price < moving_average:
        signal = "SELL"
        confidence = 0.60
        reason = "Price is below the reference moving average."
    else:
        signal = "HOLD"
        confidence = 0.50
        reason = "Price is equal to the reference moving average."

    return MarketAnalysis(
        symbol=symbol,
        timeframe=timeframe,
        signal=signal,
        confidence=confidence,
        reason=reason,
    )


def analyze_market_history(
    symbol: str,
    timeframe: str,
    prices,
    period: int,
) -> MarketAnalysis:
    from app.ai.indicators import simple_moving_average

    if not prices:
        raise ValueError("price history cannot be empty")

    mids = [price.mid for price in prices]
    current_price = mids[-1]
    moving_average = simple_moving_average(mids, period)

    return analyze_market(
        symbol=symbol,
        timeframe=timeframe,
        price=float(current_price),
        moving_average=float(moving_average),
    )

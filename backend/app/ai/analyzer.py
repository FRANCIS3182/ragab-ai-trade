from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, Sequence

from app.ai.indicators import (
    exponential_moving_average,
    relative_strength_index,
    simple_moving_average,
)
from app.ai.multi_timeframe import analyze_multi_timeframe
from app.ai.signal_fusion import fuse_signals
from app.ai.support_resistance import detect_support_resistance
from app.ai.trend import detect_trend
from app.ai.volatility import detect_volatility


Signal = Literal["BUY", "SELL", "HOLD"]


@dataclass
class MarketAnalysis:
    symbol: str
    timeframe: str
    signal: Signal
    confidence: float
    reason: str
    rsi: float | None = None
    trend: str | None = None
    volatility: str | None = None


def analyze_market(
    symbol: str,
    timeframe: str,
    price: float,
    moving_average: float,
) -> MarketAnalysis:
    """Legacy simple analyzer kept for backward compatibility."""
    if price > moving_average:
        signal: Signal = "BUY"
        confidence = 0.55
        reason = "Price is above the reference moving average."
    elif price < moving_average:
        signal = "SELL"
        confidence = 0.55
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
    period: int = 20,
) -> MarketAnalysis:
    """
    Full multi-factor analysis used by the automation engine.

    Uses:
    - SMA + EMA trend
    - RSI (14)
    - Volatility regime
    - Support / Resistance
    - Signal fusion scoring
    """
    if not prices:
        raise ValueError("price history cannot be empty")

    # Support both Decimal and objects that have .mid
    mids: list[Decimal] = []
    for p in prices:
        if hasattr(p, "mid"):
            mids.append(Decimal(str(p.mid)))
        else:
            mids.append(Decimal(str(p)))

    if len(mids) < max(period, 15):
        raise ValueError(
            f"Need at least {max(period, 15)} price points for full analysis"
        )

    current_price = mids[-1]

    # --- Indicators ---
    sma = simple_moving_average(mids, period)
    ema = exponential_moving_average(mids, period)
    rsi = relative_strength_index(mids, period=14)

    trend = detect_trend(sma=sma, ema=ema)
    volatility = detect_volatility(mids[-20:] if len(mids) >= 20 else mids)
    support_resistance = detect_support_resistance(mids)

    # Simple multi-timeframe proxy (using different periods on same series)
    short_trend = detect_trend(
        sma=simple_moving_average(mids, max(5, period // 4)),
        ema=exponential_moving_average(mids, max(5, period // 4)),
    )
    medium_trend = detect_trend(sma=sma, ema=ema)

    timeframe_signal = analyze_multi_timeframe(
        {
            "short": short_trend,
            "medium": medium_trend,
        }
    )

    # --- Fusion ---
    fusion = fuse_signals(
        trend=trend,
        volatility=volatility,
        support_resistance=support_resistance,
        timeframe_signal=timeframe_signal,
    )

    signal = fusion.signal
    confidence = fusion.confidence
    reason_parts = [fusion.reason]

    # RSI filter / override
    rsi_value = float(rsi)

    if signal == "BUY" and rsi_value > 70:
        signal = "HOLD"
        confidence *= 0.6
        reason_parts.append(f"RSI overbought ({rsi_value:.1f}) → blocked BUY")
    elif signal == "SELL" and rsi_value < 30:
        signal = "HOLD"
        confidence *= 0.6
        reason_parts.append(f"RSI oversold ({rsi_value:.1f}) → blocked SELL")
    elif signal == "BUY" and rsi_value < 35:
        confidence = min(confidence + 0.12, 0.95)
        reason_parts.append(f"RSI supportive ({rsi_value:.1f})")
    elif signal == "SELL" and rsi_value > 65:
        confidence = min(confidence + 0.12, 0.95)
        reason_parts.append(f"RSI supportive ({rsi_value:.1f})")

    # Extra confidence when price is clearly on the right side of both MAs
    if signal == "BUY" and current_price > ema and current_price > sma:
        confidence = min(confidence + 0.08, 0.95)
    elif signal == "SELL" and current_price < ema and current_price < sma:
        confidence = min(confidence + 0.08, 0.95)

    # Minimum confidence gate
    if confidence < 0.45 and signal != "HOLD":
        reason_parts.append(f"Confidence too low ({confidence:.2f}) → forced HOLD")
        signal = "HOLD"

    return MarketAnalysis(
        symbol=symbol,
        timeframe=timeframe,
        signal=signal,
        confidence=round(float(confidence), 4),
        reason=" | ".join(reason_parts),
        rsi=rsi_value,
        trend=trend,
        volatility=volatility,
    )

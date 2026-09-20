from dataclasses import dataclass
from typing import Literal


Signal = Literal["BUY", "SELL", "HOLD"]


@dataclass(frozen=True)
class SignalFusionResult:
    signal: Signal
    confidence: float
    reason: str


def fuse_signals(
    trend: Literal["UP", "DOWN", "SIDEWAYS"],
    volatility: Literal["LOW", "MEDIUM", "HIGH"],
    support_resistance: Literal["SUPPORT", "RESISTANCE"],
    timeframe_signal: Literal["UP", "DOWN", "SIDEWAYS"],
) -> SignalFusionResult:
    score = 0

    # Primary direction from trend.
    if trend == "UP":
        score += 1
    elif trend == "DOWN":
        score -= 1

    # Multi-timeframe agreement carries additional weight.
    if timeframe_signal == "UP":
        score += 2
    elif timeframe_signal == "DOWN":
        score -= 2

    # Support/resistance provides directional context.
    if support_resistance == "SUPPORT":
        score += 1
    elif support_resistance == "RESISTANCE":
        score -= 1

    # High volatility reduces confidence rather than changing direction.
    if score > 0:
        signal: Signal = "BUY"
    elif score < 0:
        signal = "SELL"
    else:
        signal = "HOLD"

    confidence = min(abs(score) / 4, 1.0)

    if volatility == "HIGH":
        confidence *= 0.75
    elif volatility == "MEDIUM":
        confidence *= 0.90

    reason = (
        f"Trend={trend}, volatility={volatility}, "
        f"support_resistance={support_resistance}, "
        f"timeframe_signal={timeframe_signal}, score={score}."
    )

    return SignalFusionResult(
        signal=signal,
        confidence=round(confidence, 4),
        reason=reason,
    )

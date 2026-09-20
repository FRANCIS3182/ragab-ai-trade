from decimal import Decimal
from typing import Literal


Trend = Literal["UP", "DOWN", "SIDEWAYS"]


def detect_trend(
    sma: Decimal,
    ema: Decimal,
) -> Trend:
    if ema > sma:
        return "UP"

    if ema < sma:
        return "DOWN"

    return "SIDEWAYS"

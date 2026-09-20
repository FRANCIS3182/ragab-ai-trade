from decimal import Decimal
from typing import Literal


LevelType = Literal["SUPPORT", "RESISTANCE"]


def detect_support_resistance(
    prices: list[Decimal],
) -> LevelType:
    if len(prices) < 3:
        raise ValueError("at least three prices are required")

    previous_price = prices[-3]
    current_price = prices[-2]
    next_price = prices[-1]

    # Local low: potential support
    if current_price <= previous_price and current_price <= next_price:
        return "SUPPORT"

    # Local high: potential resistance
    if current_price >= previous_price and current_price >= next_price:
        return "RESISTANCE"

    # No clear swing level: use the latest movement direction
    if next_price > current_price:
        return "RESISTANCE"

    return "SUPPORT"

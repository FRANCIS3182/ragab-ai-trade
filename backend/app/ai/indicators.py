from decimal import Decimal
from typing import Sequence


def simple_moving_average(
    prices: Sequence[Decimal],
    period: int,
) -> Decimal:
    if period <= 0:
        raise ValueError("period must be greater than zero")

    if len(prices) < period:
        raise ValueError("not enough prices for the requested period")

    window = prices[-period:]

    return sum(window, Decimal("0")) / Decimal(period)


def exponential_moving_average(
    prices: Sequence[Decimal],
    period: int,
) -> Decimal:
    if period <= 0:
        raise ValueError("period must be greater than zero")

    if len(prices) < period:
        raise ValueError("not enough prices for the requested period")

    multiplier = Decimal("2") / Decimal(period + 1)

    ema = sum(prices[:period], Decimal("0")) / Decimal(period)

    for price in prices[period:]:
        ema = (
            (price - ema) * multiplier
        ) + ema

    return ema

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

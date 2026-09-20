from decimal import Decimal
from typing import Literal


Volatility = Literal["LOW", "MEDIUM", "HIGH"]


def detect_volatility(
    prices: list[Decimal],
) -> Volatility:
    if len(prices) < 2:
        raise ValueError("at least two prices are required")

    change = abs(prices[-1] - prices[0])

    if change < Decimal("5"):
        return "LOW"

    if change < Decimal("20"):
        return "MEDIUM"

    return "HIGH"

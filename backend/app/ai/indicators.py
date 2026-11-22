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
        ema = ((price - ema) * multiplier) + ema

    return ema


def relative_strength_index(
    prices: Sequence[Decimal],
    period: int = 14,
) -> Decimal:
    """Classic RSI (Wilder). Returns value between 0 and 100."""
    if period <= 0:
        raise ValueError("period must be greater than zero")

    if len(prices) < period + 1:
        raise ValueError("not enough prices for RSI calculation")

    gains: list[Decimal] = []
    losses: list[Decimal] = []

    for i in range(1, len(prices)):
        change = prices[i] - prices[i - 1]
        if change > 0:
            gains.append(change)
            losses.append(Decimal("0"))
        else:
            gains.append(Decimal("0"))
            losses.append(abs(change))

    # First average (simple)
    avg_gain = sum(gains[:period], Decimal("0")) / Decimal(period)
    avg_loss = sum(losses[:period], Decimal("0")) / Decimal(period)

    # Wilder smoothing for the rest
    for i in range(period, len(gains)):
        avg_gain = ((avg_gain * (period - 1)) + gains[i]) / Decimal(period)
        avg_loss = ((avg_loss * (period - 1)) + losses[i]) / Decimal(period)

    if avg_loss == 0:
        return Decimal("100")

    rs = avg_gain / avg_loss
    rsi = Decimal("100") - (Decimal("100") / (Decimal("1") + rs))
    return rsi.quantize(Decimal("0.01"))


def average_true_range(
    highs: Sequence[Decimal],
    lows: Sequence[Decimal],
    closes: Sequence[Decimal],
    period: int = 14,
) -> Decimal:
    """Simplified ATR using high-low-close series."""
    if len(highs) != len(lows) or len(highs) != len(closes):
        raise ValueError("highs, lows and closes must have the same length")

    if len(closes) < period + 1:
        raise ValueError("not enough data for ATR")

    true_ranges: list[Decimal] = []

    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )
        true_ranges.append(tr)

    return simple_moving_average(true_ranges, period)


def atr_percent(
    atr: Decimal,
    price: Decimal,
) -> Decimal:
    """ATR as percentage of current price (useful for volatility filters)."""
    if price <= 0:
        raise ValueError("price must be positive")
    return (atr / price) * Decimal("100")

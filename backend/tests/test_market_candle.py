from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.services.market_candle import MarketCandle
from app.services.timeframes import normalize_timeframe


def test_market_candle_stores_ohlc_data():
    timestamp = datetime(2026, 9, 20, tzinfo=timezone.utc)

    candle = MarketCandle(
        symbol="XAU/USD",
        timeframe="M5",
        timestamp=timestamp,
        open=Decimal("3400"),
        high=Decimal("3410"),
        low=Decimal("3395"),
        close=Decimal("3405"),
        volume=Decimal("123.45"),
    )

    assert candle.symbol == "XAU/USD"
    assert candle.timeframe == "M5"
    assert candle.timestamp == timestamp
    assert candle.open == Decimal("3400")
    assert candle.high == Decimal("3410")
    assert candle.low == Decimal("3395")
    assert candle.close == Decimal("3405")
    assert candle.volume == Decimal("123.45")


@pytest.mark.parametrize(
    ("internal", "external"),
    [
        ("M1", "1min"),
        ("M5", "5min"),
        ("M15", "15min"),
        ("M30", "30min"),
        ("H1", "1h"),
        ("H4", "4h"),
        ("D1", "1day"),
    ],
)
def test_normalize_timeframe(internal, external):
    assert normalize_timeframe(internal) == external


def test_normalize_timeframe_accepts_lowercase_and_whitespace():
    assert normalize_timeframe(" m5 ") == "5min"


def test_normalize_timeframe_rejects_unknown_value():
    with pytest.raises(ValueError, match="Unsupported timeframe"):
        normalize_timeframe("M2")

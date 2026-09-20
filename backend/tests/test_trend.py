from decimal import Decimal

from app.ai.trend import detect_trend


def test_detect_uptrend():
    assert detect_trend(
        sma=Decimal("3400"),
        ema=Decimal("3405"),
    ) == "UP"


def test_detect_downtrend():
    assert detect_trend(
        sma=Decimal("3405"),
        ema=Decimal("3400"),
    ) == "DOWN"


def test_detect_sideways_trend():
    assert detect_trend(
        sma=Decimal("3400"),
        ema=Decimal("3400"),
    ) == "SIDEWAYS"

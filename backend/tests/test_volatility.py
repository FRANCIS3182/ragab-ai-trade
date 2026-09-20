from decimal import Decimal

import pytest

from app.ai.volatility import detect_volatility


def test_detect_low_volatility():
    assert detect_volatility(
        [Decimal("3400"), Decimal("3403")]
    ) == "LOW"


def test_detect_medium_volatility():
    assert detect_volatility(
        [Decimal("3400"), Decimal("3410")]
    ) == "MEDIUM"


def test_detect_high_volatility():
    assert detect_volatility(
        [Decimal("3400"), Decimal("3425")]
    ) == "HIGH"


def test_detect_volatility_requires_two_prices():
    with pytest.raises(ValueError, match="at least two prices"):
        detect_volatility([Decimal("3400")])

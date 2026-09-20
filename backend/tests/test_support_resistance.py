from decimal import Decimal

import pytest

from app.ai.support_resistance import detect_support_resistance


def test_detect_support():
    assert detect_support_resistance(
        [
            Decimal("3410"),
            Decimal("3400"),
            Decimal("3412"),
        ]
    ) == "SUPPORT"


def test_detect_resistance():
    assert detect_support_resistance(
        [
            Decimal("3390"),
            Decimal("3405"),
            Decimal("3395"),
        ]
    ) == "RESISTANCE"


def test_detect_support_from_downward_movement():
    assert detect_support_resistance(
        [
            Decimal("3410"),
            Decimal("3405"),
            Decimal("3400"),
        ]
    ) == "SUPPORT"


def test_detect_resistance_from_upward_movement():
    assert detect_support_resistance(
        [
            Decimal("3390"),
            Decimal("3395"),
            Decimal("3400"),
        ]
    ) == "RESISTANCE"


def test_detect_support_resistance_requires_three_prices():
    with pytest.raises(ValueError, match="at least three prices"):
        detect_support_resistance(
            [
                Decimal("3400"),
                Decimal("3410"),
            ]
        )

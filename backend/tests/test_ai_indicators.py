from decimal import Decimal

from app.ai.indicators import simple_moving_average


def test_simple_moving_average():
    prices = [
        Decimal("3390"),
        Decimal("3400"),
        Decimal("3410"),
        Decimal("3420"),
    ]

    assert simple_moving_average(prices, 3) == Decimal("3410")
    assert simple_moving_average(prices, 2) == Decimal("3415")


def test_simple_moving_average_invalid_period():
    prices = [
        Decimal("3390"),
        Decimal("3400"),
        Decimal("3410"),
        Decimal("3420"),
    ]

    try:
        simple_moving_average(prices, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("period=0 should raise ValueError")


def test_simple_moving_average_insufficient_prices():
    prices = [
        Decimal("3390"),
        Decimal("3400"),
        Decimal("3410"),
        Decimal("3420"),
    ]

    try:
        simple_moving_average(prices, 5)
    except ValueError:
        pass
    else:
        raise AssertionError("insufficient prices should raise ValueError")

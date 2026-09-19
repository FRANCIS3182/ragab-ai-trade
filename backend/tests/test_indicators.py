

def test_exponential_moving_average():
    from decimal import Decimal

    from app.ai.indicators import exponential_moving_average

    prices = [
        Decimal("10"),
        Decimal("11"),
        Decimal("12"),
        Decimal("13"),
        Decimal("14"),
    ]

    result = exponential_moving_average(prices, 3)

    assert result == Decimal("13.00")


def test_exponential_moving_average_rejects_invalid_period():
    from decimal import Decimal

    import pytest

    from app.ai.indicators import exponential_moving_average

    prices = [Decimal("10"), Decimal("11"), Decimal("12")]

    with pytest.raises(ValueError, match="period"):
        exponential_moving_average(prices, 0)


def test_exponential_moving_average_requires_enough_prices():
    from decimal import Decimal

    import pytest

    from app.ai.indicators import exponential_moving_average

    prices = [Decimal("10"), Decimal("11")]

    with pytest.raises(ValueError, match="not enough prices"):
        exponential_moving_average(prices, 3)

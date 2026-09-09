from decimal import Decimal

from app.ai.indicators import simple_moving_average


def main():
    prices = [
        Decimal("3390"),
        Decimal("3400"),
        Decimal("3410"),
        Decimal("3420"),
    ]

    assert simple_moving_average(prices, 3) == Decimal("3410")
    assert simple_moving_average(prices, 2) == Decimal("3415")

    try:
        simple_moving_average(prices, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("period=0 should raise ValueError")

    try:
        simple_moving_average(prices, 5)
    except ValueError:
        pass
    else:
        raise AssertionError("insufficient prices should raise ValueError")

    print("AI_INDICATORS_TEST_OK")


if __name__ == "__main__":
    main()

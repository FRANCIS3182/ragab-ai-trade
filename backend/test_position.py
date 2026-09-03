from decimal import Decimal

from app.services.position_service import (
    calculate_realized_pnl,
    calculate_unrealized_pnl,
    calculate_weighted_average_entry,
)


def main():
    realized = calculate_realized_pnl(
        side="buy",
        quantity=Decimal("0.005"),
        entry_price=Decimal("3400"),
        exit_price=Decimal("3410"),
    )

    unrealized = calculate_unrealized_pnl(
        side="buy",
        quantity=Decimal("0.005"),
        entry_price=Decimal("3400"),
        current_price=Decimal("3410"),
    )

    average = calculate_weighted_average_entry(
        old_quantity=Decimal("0.010"),
        old_entry_price=Decimal("3400"),
        new_quantity=Decimal("0.010"),
        new_entry_price=Decimal("3420"),
    )

    assert realized == Decimal("0.050")
    assert unrealized == Decimal("0.050")
    assert average == Decimal("3410")

    print("POSITION_TEST_OK")
    print(f"REALIZED P/L: {realized}")
    print(f"UNREALIZED P/L: {unrealized}")
    print(f"WEIGHTED ENTRY: {average}")


if __name__ == "__main__":
    main()

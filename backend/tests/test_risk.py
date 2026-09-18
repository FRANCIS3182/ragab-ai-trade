from decimal import Decimal

def test_risk_calculation():
    price = Decimal("3400")
    stop_loss = Decimal("3390")

    risk = abs(price - stop_loss) * Decimal("10")
    maximum_risk = Decimal("10000") * Decimal("1") / Decimal("100")

    assert risk == Decimal("100")
    assert risk <= maximum_risk

    excessive_risk = abs(price - stop_loss) * Decimal("10.001")
    assert excessive_risk > maximum_risk

    print("RISK_BOUNDARY_TEST_OK")
    print(f"MAXIMUM RISK: {maximum_risk}")
    print(f"EXACT RISK: {risk}")
    print(f"EXCESSIVE RISK: {excessive_risk}")

if __name__ == "__main__":
    test_risk_calculation()

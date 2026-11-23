from decimal import Decimal

import pytest

from app.ai.trade_setup import create_trade_setup


def test_buy_trade_setup():
    result = create_trade_setup(
        signal="BUY",
        entry_price=Decimal("3400"),
        confidence=0.80,
        risk_distance=Decimal("10"),
        reward_multiple=Decimal("2"),
    )

    assert result.signal == "BUY"
    assert result.entry_price == Decimal("3400")
    assert result.stop_loss == Decimal("3390")
    assert result.take_profit == Decimal("3420")
    assert result.risk_reward_ratio == Decimal("2")
    assert result.confidence == 0.80


def test_sell_trade_setup():
    result = create_trade_setup(
        signal="SELL",
        entry_price=Decimal("3400"),
        confidence=0.80,
        risk_distance=Decimal("10"),
        reward_multiple=Decimal("2"),
    )

    assert result.signal == "SELL"
    assert result.entry_price == Decimal("3400")
    assert result.stop_loss == Decimal("3410")
    assert result.take_profit == Decimal("3380")


def test_low_confidence_still_creates_setup():
    result = create_trade_setup(
        signal="BUY",
        entry_price=Decimal("3400"),
        confidence=0.40,
        risk_distance=Decimal("10"),
        reward_multiple=Decimal("2"),
    )

    assert result.signal == "BUY"
    assert result.confidence == 0.40


def test_zero_risk_distance_rejected():
    with pytest.raises(ValueError, match="risk distance"):
        create_trade_setup(
            signal="BUY",
            entry_price=Decimal("3400"),
            confidence=0.80,
            risk_distance=Decimal("0"),
            reward_multiple=Decimal("2"),
        )


def test_invalid_signal_behavior():
    result = create_trade_setup(
        signal="HOLD",
        entry_price=Decimal("3400"),
        confidence=0.80,
        risk_distance=Decimal("10"),
        reward_multiple=Decimal("2"),
    )

    assert result.signal == "HOLD"
    assert result.stop_loss == Decimal("3410")
    assert result.take_profit == Decimal("3380")


def test_reward_multiple():
    result = create_trade_setup(
        signal="BUY",
        entry_price=Decimal("3400"),
        confidence=0.90,
        risk_distance=Decimal("5"),
        reward_multiple=Decimal("3"),
    )

    assert result.stop_loss == Decimal("3395")
    assert result.take_profit == Decimal("3415")
    assert result.risk_reward_ratio == Decimal("3")

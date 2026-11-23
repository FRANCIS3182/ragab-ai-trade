from dataclasses import dataclass
from decimal import Decimal
from typing import Literal


Signal = Literal["BUY", "SELL"]


@dataclass(frozen=True)
class TradeSetup:
    signal: Signal
    entry_price: Decimal
    stop_loss: Decimal
    take_profit: Decimal
    risk_reward_ratio: Decimal
    confidence: float
    reason: str


def create_trade_setup(
    signal: Signal,
    entry_price: Decimal,
    confidence: float,
    risk_distance: Decimal,
    reward_multiple: Decimal = Decimal("2"),
) -> TradeSetup:
    if entry_price <= 0:
        raise ValueError("entry price must be greater than zero")

    if risk_distance <= 0:
        raise ValueError("risk distance must be greater than zero")

    if reward_multiple <= 0:
        raise ValueError("reward multiple must be greater than zero")

    if not 0 <= confidence <= 1:
        raise ValueError("confidence must be between 0 and 1")

    if signal == "BUY":
        stop_loss = entry_price - risk_distance
        take_profit = entry_price + (
            risk_distance * reward_multiple
        )
    else:
        stop_loss = entry_price + risk_distance
        take_profit = entry_price - (
            risk_distance * reward_multiple
        )

    return TradeSetup(
        signal=signal,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        risk_reward_ratio=reward_multiple,
        confidence=confidence,
        reason=(
            f"{signal} setup with {reward_multiple}:1 "
            "risk/reward target."
        ),
    )

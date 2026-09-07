from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.position import Position
from app.models.realized_pnl_event import RealizedPnlEvent


def calculate_unrealized_pnl(
    side: str,
    quantity: Decimal,
    entry_price: Decimal,
    current_price: Decimal,
) -> Decimal:
    if side == "buy":
        return (current_price - entry_price) * quantity

    if side == "sell":
        return (entry_price - current_price) * quantity

    raise ValueError("Position side must be buy or sell")


def calculate_weighted_average_entry(
    old_quantity: Decimal,
    old_entry_price: Decimal,
    new_quantity: Decimal,
    new_entry_price: Decimal,
) -> Decimal:
    total_quantity = old_quantity + new_quantity

    if total_quantity <= 0:
        raise ValueError("Total quantity must be greater than zero")

    return (
        (old_quantity * old_entry_price)
        + (new_quantity * new_entry_price)
    ) / total_quantity


async def update_position_price(
    db: AsyncSession,
    position: Position,
    current_price: Decimal,
) -> Position:
    position.current_price = current_price
    position.unrealized_pnl = calculate_unrealized_pnl(
        side=position.side,
        quantity=position.quantity,
        entry_price=position.entry_price,
        current_price=current_price,
    )

    await db.flush()
    return position


async def get_open_position(
    db: AsyncSession,
    trading_account_id,
    symbol: str,
    side: str,
) -> Position | None:
    result = await db.execute(
        select(Position)
        .where(
            Position.trading_account_id == trading_account_id,
            Position.symbol == symbol.upper(),
            Position.side == side,
            Position.status == "open",
        )
        .order_by(Position.opened_at.asc())
        .limit(1)
    )

    return result.scalar_one_or_none()


async def add_to_position(
    db: AsyncSession,
    position: Position,
    quantity: Decimal,
    entry_price: Decimal,
) -> Position:
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")

    if position.status != "open":
        raise ValueError("Cannot add to a closed position")

    if position.side not in ("buy", "sell"):
        raise ValueError("Position side must be buy or sell")

    position.entry_price = calculate_weighted_average_entry(
        old_quantity=position.quantity,
        old_entry_price=position.entry_price,
        new_quantity=quantity,
        new_entry_price=entry_price,
    )

    position.quantity += quantity
    position.current_price = entry_price
    position.unrealized_pnl = calculate_unrealized_pnl(
        side=position.side,
        quantity=position.quantity,
        entry_price=position.entry_price,
        current_price=position.current_price,
    )

    await db.flush()
    return position


def calculate_realized_pnl(
    side: str,
    quantity: Decimal,
    entry_price: Decimal,
    exit_price: Decimal,
) -> Decimal:
    if side == "buy":
        return (exit_price - entry_price) * quantity

    if side == "sell":
        return (entry_price - exit_price) * quantity

    raise ValueError("Position side must be buy or sell")


async def close_position(
    db: AsyncSession,
    position: Position,
    quantity: Decimal,
    exit_price: Decimal,
) -> Decimal:
    if position.status != "open":
        raise ValueError("Position is already closed")

    if quantity <= 0:
        raise ValueError("Close quantity must be greater than zero")

    if quantity > position.quantity:
        raise ValueError("Close quantity cannot exceed position quantity")

    realized = calculate_realized_pnl(
        side=position.side,
        quantity=quantity,
        entry_price=position.entry_price,
        exit_price=exit_price,
    )

    db.add(
        RealizedPnlEvent(
            trading_account_id=position.trading_account_id,
            position_id=position.id,
            realized_pnl=realized,
        )
    )

    position.realized_pnl += realized
    position.quantity -= quantity
    position.current_price = exit_price

    if position.quantity == 0:
        position.status = "closed"
        position.closed_at = datetime.now(timezone.utc)
        position.unrealized_pnl = Decimal("0")
    else:
        position.unrealized_pnl = calculate_unrealized_pnl(
            side=position.side,
            quantity=position.quantity,
            entry_price=position.entry_price,
            current_price=exit_price,
        )

    await db.flush()
    return realized


async def execute_opposite_order(
    db: AsyncSession,
    position: Position,
    quantity: Decimal,
    exit_price: Decimal,
) -> Position:
    if position.status != "open":
        raise ValueError("Position is already closed")

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")

    if quantity > position.quantity:
        raise ValueError("Opposite order quantity exceeds position quantity")

    return await close_position(
        db=db,
        position=position,
        quantity=quantity,
        exit_price=exit_price,
    )

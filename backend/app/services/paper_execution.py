from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.order import Order
from app.models.position import Position
from app.models.trading_account import TradingAccount
from app.services.position_service import (
    add_to_position,
    close_position,
    get_open_position,
)
from app.services.risk_service import validate_paper_order_risk


async def execute_paper_order(
    db: AsyncSession,
    account: TradingAccount,
    symbol: str,
    side: str,
    quantity: Decimal,
    price: Decimal | None = None,
    stop_loss: Decimal | None = None,
) -> Order:
    if not settings.paper_trading_only:
        raise ValueError(
            "Paper-trading safety flag is disabled"
        )

    symbol = symbol.upper()

    await validate_paper_order_risk(
        db=db,
        trading_account_id=account.id,
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
        stop_loss=stop_loss,
    )

    order = Order(
        trading_account_id=account.id,
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
        stop_loss=stop_loss,
        status="simulated",
    )

    db.add(order)

    if price is not None:
        existing_position = await get_open_position(
            db=db,
            trading_account_id=account.id,
            symbol=symbol,
            side=side,
        )

        if existing_position:
            await add_to_position(
                db=db,
                position=existing_position,
                quantity=quantity,
                entry_price=price,
            )

            if stop_loss is not None:
                existing_position.stop_loss = stop_loss
        else:
            opposite_side = "sell" if side == "buy" else "buy"

            opposite_position = await get_open_position(
                db=db,
                trading_account_id=account.id,
                symbol=symbol,
                side=opposite_side,
            )

            if opposite_position:
                if quantity > opposite_position.quantity:
                    raise ValueError(
                        "Opposite order exceeds existing position. "
                        "Position reversal will be enabled in a later step."
                    )

                realized_pnl = await close_position(
                    db=db,
                    position=opposite_position,
                    quantity=quantity,
                    exit_price=price,
                )

                account.balance = (
                    account.balance or Decimal("0")
                ) + realized_pnl
            else:
                position = Position(
                    trading_account_id=account.id,
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    entry_price=price,
                    current_price=price,
                    stop_loss=stop_loss,
                    unrealized_pnl=Decimal("0"),
                    realized_pnl=Decimal("0"),
                    status="open",
                )

                db.add(position)

    await db.commit()
    await db.refresh(order)

    return order

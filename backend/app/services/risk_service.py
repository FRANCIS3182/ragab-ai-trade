from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.position import Position
from app.models.realized_pnl_event import RealizedPnlEvent
from app.models.risk_setting import RiskSetting
from app.models.trading_account import TradingAccount


async def get_or_create_risk_setting(
    db: AsyncSession,
    trading_account_id: UUID,
) -> RiskSetting:
    result = await db.execute(
        select(RiskSetting).where(
            RiskSetting.trading_account_id == trading_account_id
        )
    )

    setting = result.scalar_one_or_none()

    if setting is None:
        setting = RiskSetting(
            trading_account_id=trading_account_id,
        )
        db.add(setting)
        await db.flush()

    return setting


async def validate_paper_order_risk(
    db: AsyncSession,
    trading_account_id: UUID,
    symbol: str,
    side: str,
    quantity: Decimal,
    price: Decimal | None = None,
    stop_loss: Decimal | None = None,
) -> None:
    if quantity <= 0:
        raise ValueError("Order quantity must be greater than zero")

    if side not in ("buy", "sell"):
        raise ValueError("Order side must be buy or sell")

    setting = await get_or_create_risk_setting(
        db=db,
        trading_account_id=trading_account_id,
    )

    account_result = await db.execute(
        select(TradingAccount).where(
            TradingAccount.id == trading_account_id
        )
    )

    account = account_result.scalar_one_or_none()

    if account is None:
        raise ValueError("Trading account not found")

    balance = account.balance or Decimal("0")

    unrealized_result = await db.execute(
        select(
            func.coalesce(
                func.sum(Position.unrealized_pnl),
                Decimal("0"),
            )
        ).where(
            Position.trading_account_id == account.id,
            Position.status == "open",
        )
    )

    unrealized_pnl = unrealized_result.scalar_one() or Decimal("0")
    equity = balance + unrealized_pnl

    day_start = datetime.now(timezone.utc).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    daily_loss_result = await db.execute(
        select(
            func.coalesce(
                func.sum(RealizedPnlEvent.realized_pnl),
                Decimal("0"),
            )
        ).where(
            RealizedPnlEvent.trading_account_id == trading_account_id,
            RealizedPnlEvent.realized_at >= day_start,
            RealizedPnlEvent.realized_pnl < 0,
        )
    )

    daily_loss = abs(
        daily_loss_result.scalar_one() or Decimal("0")
    )

    maximum_daily_loss = (
        balance * setting.max_daily_loss_pct / Decimal("100")
    )

    if daily_loss >= maximum_daily_loss:
        raise ValueError(
            "Daily loss limit reached: "
            f"{setting.max_daily_loss_pct}% "
            f"(${maximum_daily_loss:.2f})"
        )

    if stop_loss is not None:
        if price is None:
            raise ValueError(
                "Entry price is required when stop-loss is provided"
            )

        if side == "buy" and stop_loss >= price:
            raise ValueError(
                "Buy stop-loss must be below the entry price"
            )

        if side == "sell" and stop_loss <= price:
            raise ValueError(
                "Sell stop-loss must be above the entry price"
            )

        maximum_risk = (
            equity * setting.max_risk_per_trade_pct / Decimal("100")
        )

        risk_per_unit = abs(price - stop_loss)
        total_risk = risk_per_unit * quantity

        if total_risk > maximum_risk:
            raise ValueError(
                "Trade risk exceeds the maximum allowed risk of "
                f"{setting.max_risk_per_trade_pct}% "
                f"(${maximum_risk:.2f})"
            )

    open_positions_result = await db.execute(
        select(func.count(Position.id)).where(
            Position.trading_account_id == trading_account_id,
            Position.status == "open",
        )
    )

    open_positions = open_positions_result.scalar_one() or 0

    existing_same_side_result = await db.execute(
        select(Position.id).where(
            Position.trading_account_id == trading_account_id,
            Position.symbol == symbol.upper(),
            Position.side == side,
            Position.status == "open",
        ).limit(1)
    )

    existing_same_side = existing_same_side_result.scalar_one_or_none()

    if (
        existing_same_side is None
        and open_positions >= setting.max_open_positions
    ):
        raise ValueError(
            f"Maximum open positions reached ({setting.max_open_positions})"
        )

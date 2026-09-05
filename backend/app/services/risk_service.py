from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.position import Position
from app.models.risk_setting import RiskSetting


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
) -> None:
    if quantity <= 0:
        raise ValueError("Order quantity must be greater than zero")

    if side not in ("buy", "sell"):
        raise ValueError("Order side must be buy or sell")

    setting = await get_or_create_risk_setting(
        db=db,
        trading_account_id=trading_account_id,
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

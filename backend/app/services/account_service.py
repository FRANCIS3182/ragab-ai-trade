from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.position import Position
from app.models.trading_account import TradingAccount


async def get_paper_account_summary(
    db: AsyncSession,
    trading_account_id: UUID,
    user_id: UUID,
) -> dict:
    account_result = await db.execute(
        select(TradingAccount).where(
            TradingAccount.id == trading_account_id,
            TradingAccount.user_id == user_id,
            TradingAccount.mode == "paper",
            TradingAccount.is_active.is_(True),
        )
    )

    account = account_result.scalar_one_or_none()

    if account is None:
        raise ValueError("Paper trading account not found")

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
    balance = account.balance or Decimal("0")
    equity = balance + unrealized_pnl

    return {
        "id": account.id,
        "name": account.name,
        "mode": account.mode,
        "currency": account.currency,
        "balance": balance,
        "unrealized_pnl": unrealized_pnl,
        "equity": equity,
        "available_funds": equity,
        "is_active": account.is_active,
    }

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.db.session import get_db
from app.models.position import Position
from app.models.trading_account import TradingAccount
from app.models.user import User
from app.schemas.position import PositionResponse

router = APIRouter()


@router.get("", response_model=list[PositionResponse])
async def list_paper_positions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Position)
        .join(
            TradingAccount,
            TradingAccount.id == Position.trading_account_id,
        )
        .where(
            TradingAccount.user_id == current_user.id,
            TradingAccount.mode == "paper",
        )
        .order_by(Position.opened_at.desc())
    )

    return result.scalars().all()

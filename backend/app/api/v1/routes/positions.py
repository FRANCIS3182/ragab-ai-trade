from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.db.session import get_db
from app.models.position import Position
from app.models.trading_account import TradingAccount
from app.models.user import User
from app.services.position_service import update_position_price
from app.schemas.position import PositionPriceUpdate, PositionResponse

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


@router.post("/{position_id}/price", response_model=PositionResponse)
async def update_paper_position_price(
    position_id: UUID,
    payload: PositionPriceUpdate,
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
            Position.id == position_id,
            TradingAccount.user_id == current_user.id,
            TradingAccount.mode == "paper",
            TradingAccount.is_active.is_(True),
        )
    )

    position = result.scalar_one_or_none()

    if position is None:
        raise HTTPException(
            status_code=404,
            detail="Paper position not found",
        )

    try:
        await update_position_price(
            db=db,
            position=position,
            current_price=payload.current_price,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    await db.commit()
    await db.refresh(position)

    return position

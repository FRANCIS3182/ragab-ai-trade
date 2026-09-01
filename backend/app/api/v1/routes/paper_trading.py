from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.order import Order
from app.models.trading_account import TradingAccount
from app.models.user import User
from app.schemas.order import OrderResponse, PaperOrderCreate

router = APIRouter()


@router.post("/orders", response_model=OrderResponse, status_code=201)
async def create_paper_order(
    payload: PaperOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not settings.paper_trading_only:
        raise HTTPException(
            status_code=503,
            detail="Paper-trading safety flag is disabled",
        )

    result = await db.execute(
        select(TradingAccount).where(
            TradingAccount.id == payload.trading_account_id,
            TradingAccount.user_id == current_user.id,
            TradingAccount.is_active.is_(True),
            TradingAccount.mode == "paper",
        )
    )

    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Paper trading account not found",
        )

    order = Order(
        trading_account_id=account.id,
        symbol=payload.symbol.upper(),
        side=payload.side,
        quantity=payload.quantity,
        price=payload.price,
        status="simulated",
    )

    db.add(order)
    await db.commit()
    await db.refresh(order)

    return order

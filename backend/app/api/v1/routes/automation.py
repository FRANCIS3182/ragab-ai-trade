from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.db.session import get_db
from app.models.trading_account import TradingAccount
from app.models.user import User
from app.services.ai_trading import run_ai_paper_trade

router = APIRouter()


class AutomationRequest(BaseModel):
    trading_account_id: UUID
    symbol: str = Field(min_length=2, max_length=30)
    timeframe: str = Field(min_length=1, max_length=10)
    price: Decimal = Field(gt=0)
    moving_average: Decimal = Field(gt=0)
    quantity: Decimal = Field(gt=0)


@router.post("/run")
async def run_automation(
    payload: AutomationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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

    try:
        automation = await run_ai_paper_trade(
            db=db,
            account=account,
            symbol=payload.symbol,
            timeframe=payload.timeframe,
            price=payload.price,
            moving_average=payload.moving_average,
            quantity=payload.quantity,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    return {
        "signal": automation.signal,
        "confidence": automation.confidence,
        "reason": automation.reason,
        "order_id": automation.order_id,
        "status": automation.status,
        "execution": "paper_only",
    }

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.v1.dependencies import get_current_user
from app.db.session import get_db
from app.models.trading_account import TradingAccount
from app.models.user import User
from app.services.account_service import get_paper_account_summary
from app.schemas.account_summary import PaperAccountSummaryResponse
from app.schemas.trading_account import (
    TradingAccountCreate,
    TradingAccountResponse,
)

router = APIRouter()


@router.post(
    "",
    response_model=TradingAccountResponse,
    status_code=201,
)
async def create_trading_account(
    payload: TradingAccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = TradingAccount(
        user_id=current_user.id,
        name=payload.name,
        mode="paper",
        currency=payload.currency.upper(),
        balance=payload.balance,
        is_active=True,
    )

    db.add(account)
    await db.commit()
    await db.refresh(account)

    return account


@router.get(
    "/{trading_account_id}/summary",
    response_model=PaperAccountSummaryResponse,
)
async def get_trading_account_summary(
    trading_account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await get_paper_account_summary(
            db=db,
            trading_account_id=trading_account_id,
            user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

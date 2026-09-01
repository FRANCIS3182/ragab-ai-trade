from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.db.session import get_db
from app.models.trading_account import TradingAccount
from app.models.user import User
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

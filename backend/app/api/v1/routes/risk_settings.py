from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.db.session import get_db
from app.models.risk_setting import RiskSetting
from app.models.trading_account import TradingAccount
from app.models.user import User
from app.schemas.risk_setting import (
    RiskSettingResponse,
    RiskSettingUpdate,
)

router = APIRouter()


@router.get(
    "/{trading_account_id}",
    response_model=RiskSettingResponse,
)
async def get_risk_settings(
    trading_account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account_result = await db.execute(
        select(TradingAccount).where(
            TradingAccount.id == trading_account_id,
            TradingAccount.user_id == current_user.id,
        )
    )

    account = account_result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Trading account not found",
        )

    result = await db.execute(
        select(RiskSetting).where(
            RiskSetting.trading_account_id == trading_account_id
        )
    )

    setting = result.scalar_one_or_none()

    if not setting:
        setting = RiskSetting(
            trading_account_id=trading_account_id
        )
        db.add(setting)
        await db.commit()
        await db.refresh(setting)

    return setting


@router.put(
    "/{trading_account_id}",
    response_model=RiskSettingResponse,
)
async def update_risk_settings(
    trading_account_id: UUID,
    payload: RiskSettingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account_result = await db.execute(
        select(TradingAccount).where(
            TradingAccount.id == trading_account_id,
            TradingAccount.user_id == current_user.id,
        )
    )

    account = account_result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Trading account not found",
        )

    result = await db.execute(
        select(RiskSetting).where(
            RiskSetting.trading_account_id == trading_account_id
        )
    )

    setting = result.scalar_one_or_none()

    if not setting:
        setting = RiskSetting(
            trading_account_id=trading_account_id
        )
        db.add(setting)

    setting.max_risk_per_trade_pct = payload.max_risk_per_trade_pct
    setting.max_daily_loss_pct = payload.max_daily_loss_pct
    setting.max_open_positions = payload.max_open_positions

    await db.commit()
    await db.refresh(setting)

    return setting

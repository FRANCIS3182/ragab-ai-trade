from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.order import Order
from app.models.position import Position
from app.models.trading_account import TradingAccount
from app.models.user import User
from app.services.position_service import add_to_position, get_open_position, close_position
from app.services.risk_service import validate_paper_order_risk
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

    symbol = payload.symbol.upper()

    try:
        await validate_paper_order_risk(
            db=db,
            trading_account_id=account.id,
            symbol=symbol,
            side=payload.side,
            quantity=payload.quantity,
            price=payload.price,
            stop_loss=payload.stop_loss,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    order = Order(
        trading_account_id=account.id,
        symbol=symbol,
        side=payload.side,
        quantity=payload.quantity,
        price=payload.price,
        stop_loss=payload.stop_loss,
        status="simulated",
    )

    db.add(order)

    if payload.price is not None:
        existing_position = await get_open_position(
            db=db,
            trading_account_id=account.id,
            symbol=symbol,
            side=payload.side,
        )

        if existing_position:
            await add_to_position(
                db=db,
                position=existing_position,
                quantity=payload.quantity,
                entry_price=payload.price,
            )
        else:
            opposite_side = "sell" if payload.side == "buy" else "buy"

            opposite_position = await get_open_position(
                db=db,
                trading_account_id=account.id,
                symbol=symbol,
                side=opposite_side,
            )

            if opposite_position:
                if payload.quantity > opposite_position.quantity:
                    raise HTTPException(
                        status_code=400,
                        detail="Opposite order exceeds existing position. "
                        "Position reversal will be enabled in a later step.",
                    )

                realized_pnl = await close_position(
                    db=db,
                    position=opposite_position,
                    quantity=payload.quantity,
                    exit_price=payload.price,
                )

                account.balance = (account.balance or 0) + realized_pnl
            else:
                position = Position(
                    trading_account_id=account.id,
                    symbol=symbol,
                    side=payload.side,
                    quantity=payload.quantity,
                    entry_price=payload.price,
                    current_price=payload.price,
                    stop_loss=payload.stop_loss,
                    unrealized_pnl=0,
                    realized_pnl=0,
                    status="open",
                )

                db.add(position)

    await db.commit()
    await db.refresh(order)

    return order


@router.get("/orders", response_model=list[OrderResponse])
async def list_paper_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Order)
        .join(TradingAccount, TradingAccount.id == Order.trading_account_id)
        .where(
            TradingAccount.user_id == current_user.id,
            TradingAccount.mode == "paper",
        )
        .order_by(Order.created_at.desc())
    )

    return result.scalars().all()

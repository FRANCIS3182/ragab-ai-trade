from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.order import Order
from app.schemas.order import OrderResponse, PaperOrderCreate
from app.core.config import settings

router = APIRouter()

@router.post("/orders", response_model=OrderResponse, status_code=201)
async def create_paper_order(payload: PaperOrderCreate, db: AsyncSession = Depends(get_db)):
    if not settings.paper_trading_only:
        raise HTTPException(status_code=503, detail="Paper-trading safety flag is disabled")
    order = Order(
        trading_account_id=payload.trading_account_id,
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

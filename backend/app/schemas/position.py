from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class PositionResponse(BaseModel):
    id: UUID
    trading_account_id: UUID
    symbol: str
    side: str
    quantity: Decimal
    entry_price: Decimal
    current_price: Decimal
    stop_loss: Decimal | None
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    status: str
    opened_at: datetime
    closed_at: datetime | None


class PositionPriceUpdate(BaseModel):
    current_price: Decimal

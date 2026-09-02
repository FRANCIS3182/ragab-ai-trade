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
    unrealized_pnl: Decimal
    status: str
    opened_at: datetime
    closed_at: datetime | None

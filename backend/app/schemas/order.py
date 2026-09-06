from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field

class PaperOrderCreate(BaseModel):
    trading_account_id: UUID
    symbol: str = Field(min_length=2, max_length=30)
    side: str = Field(pattern="^(buy|sell)$")
    quantity: Decimal = Field(gt=0)
    price: Decimal | None = Field(default=None, gt=0)
    stop_loss: Decimal | None = Field(default=None, gt=0)

class OrderResponse(BaseModel):
    id: UUID
    symbol: str
    side: str
    quantity: Decimal
    price: Decimal | None
    stop_loss: Decimal | None
    status: str

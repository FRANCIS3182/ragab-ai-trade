from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field


class TradingAccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    currency: str = Field(default="USD", min_length=3, max_length=10)
    balance: Decimal = Field(default=10000, ge=0)


class TradingAccountResponse(BaseModel):
    id: UUID
    name: str
    mode: str
    currency: str
    balance: Decimal
    is_active: bool

    model_config = {"from_attributes": True}

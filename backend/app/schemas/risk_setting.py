from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field

class RiskSettingUpdate(BaseModel):
    max_risk_per_trade_pct: Decimal = Field(gt=0, le=100)
    max_daily_loss_pct: Decimal = Field(gt=0, le=100)
    max_open_positions: int = Field(gt=0, le=100)

class RiskSettingResponse(BaseModel):
    id: UUID
    trading_account_id: UUID
    max_risk_per_trade_pct: Decimal
    max_daily_loss_pct: Decimal
    max_open_positions: int

    model_config = {"from_attributes": True}

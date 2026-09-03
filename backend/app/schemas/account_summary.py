from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class PaperAccountSummaryResponse(BaseModel):
    id: UUID
    name: str
    mode: str
    currency: str
    balance: Decimal
    unrealized_pnl: Decimal
    equity: Decimal
    available_funds: Decimal
    is_active: bool

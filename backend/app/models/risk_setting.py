from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

class RiskSetting(Base):
    __tablename__ = "risk_settings"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    trading_account_id: Mapped[UUID] = mapped_column(
        ForeignKey("trading_accounts.id", ondelete="CASCADE"), unique=True
    )
    max_risk_per_trade_pct: Mapped[Decimal] = mapped_column(Numeric(6, 3), default=1)
    max_daily_loss_pct: Mapped[Decimal] = mapped_column(Numeric(6, 3), default=3)
    max_open_positions: Mapped[int] = mapped_column(default=5)

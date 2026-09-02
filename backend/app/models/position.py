from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    trading_account_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("trading_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    symbol: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    side: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )

    entry_price: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )

    current_price: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )

    unrealized_pnl: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
        default=0,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="open",
        server_default="open",
    )

    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

"""add stop loss to positions

Revision ID: 2f9dd3f2cf83
Revises: add_realized_pnl_events
Create Date: 2026-09-07
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2f9dd3f2cf83"
down_revision: Union[str, Sequence[str], None] = "add_realized_pnl_events"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "positions",
        sa.Column(
            "stop_loss",
            sa.Numeric(20, 8),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("positions", "stop_loss")

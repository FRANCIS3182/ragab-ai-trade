"""add realized pnl events

Revision ID: add_realized_pnl_events
Revises: add_stop_loss_to_orders
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "add_realized_pnl_events"
down_revision = "add_stop_loss_to_orders"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "realized_pnl_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "trading_account_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "position_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "realized_pnl",
            sa.Numeric(20, 8),
            nullable=False,
        ),
        sa.Column(
            "realized_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["trading_account_id"],
            ["trading_accounts.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["position_id"],
            ["positions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_realized_pnl_events_trading_account_id",
        "realized_pnl_events",
        ["trading_account_id"],
    )

    op.create_index(
        "ix_realized_pnl_events_position_id",
        "realized_pnl_events",
        ["position_id"],
    )

    op.create_index(
        "ix_realized_pnl_events_realized_at",
        "realized_pnl_events",
        ["realized_at"],
    )


def downgrade():
    op.drop_index(
        "ix_realized_pnl_events_realized_at",
        table_name="realized_pnl_events",
    )
    op.drop_index(
        "ix_realized_pnl_events_position_id",
        table_name="realized_pnl_events",
    )
    op.drop_index(
        "ix_realized_pnl_events_trading_account_id",
        table_name="realized_pnl_events",
    )
    op.drop_table("realized_pnl_events")

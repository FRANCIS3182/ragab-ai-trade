"""add stop loss to orders

Revision ID: add_stop_loss_to_orders
Revises: 813034f0c615
"""

from alembic import op
import sqlalchemy as sa


revision = "add_stop_loss_to_orders"
down_revision = "813034f0c615"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "orders",
        sa.Column(
            "stop_loss",
            sa.Numeric(20, 8),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("orders", "stop_loss")

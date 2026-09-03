"""add realized pnl to positions

Revision ID: 813034f0c615
Revises: 405db43c8516
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "813034f0c615"
down_revision: Union[str, Sequence[str], None] = "405db43c8516"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "positions",
        sa.Column(
            "realized_pnl",
            sa.Numeric(20, 8),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("positions", "realized_pnl")

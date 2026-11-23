"""add take profit to orders and positions

Revision ID: fdd38fbbdf6f
Revises: 2f9dd3f2cf83
Create Date: 2026-11-22 13:43:41.850997

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'fdd38fbbdf6f'
down_revision: Union[str, Sequence[str], None] = '2f9dd3f2cf83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'orders',
        sa.Column(
            'take_profit',
            sa.Numeric(20, 8),
            nullable=True,
        ),
    )

    op.add_column(
        'positions',
        sa.Column(
            'take_profit',
            sa.Numeric(20, 8),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column('positions', 'take_profit')
    op.drop_column('orders', 'take_profit')

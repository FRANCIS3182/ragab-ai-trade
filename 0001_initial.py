from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "trading_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("mode", sa.String(20), nullable=False, server_default="paper"),
        sa.Column("currency", sa.String(10), nullable=False, server_default="USD"),
        sa.Column("balance", sa.Numeric(20, 8), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trading_accounts_user_id", "trading_accounts", ["user_id"])

    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("trading_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("trading_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("symbol", sa.String(30), nullable=False),
        sa.Column("side", sa.String(10), nullable=False),
        sa.Column("order_type", sa.String(20), nullable=False, server_default="market"),
        sa.Column("quantity", sa.Numeric(20, 8), nullable=False),
        sa.Column("price", sa.Numeric(20, 8)),
        sa.Column("status", sa.String(20), nullable=False, server_default="simulated"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_orders_trading_account_id", "orders", ["trading_account_id"])
    op.create_index("ix_orders_symbol", "orders", ["symbol"])

    op.create_table(
        "signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("symbol", sa.String(30), nullable=False),
        sa.Column("timeframe", sa.String(20), nullable=False),
        sa.Column("direction", sa.String(10), nullable=False),
        sa.Column("confidence", sa.Numeric(6, 4), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_signals_symbol", "signals", ["symbol"])

    op.create_table(
        "risk_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("trading_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("trading_accounts.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("max_risk_per_trade_pct", sa.Numeric(6, 3), nullable=False, server_default="1"),
        sa.Column("max_daily_loss_pct", sa.Numeric(6, 3), nullable=False, server_default="3"),
        sa.Column("max_open_positions", sa.Integer(), nullable=False, server_default="5"),
    )

def downgrade() -> None:
    op.drop_table("risk_settings")
    op.drop_index("ix_signals_symbol", table_name="signals")
    op.drop_table("signals")
    op.drop_index("ix_orders_symbol", table_name="orders")
    op.drop_index("ix_orders_trading_account_id", table_name="orders")
    op.drop_table("orders")
    op.drop_index("ix_trading_accounts_user_id", table_name="trading_accounts")
    op.drop_table("trading_accounts")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

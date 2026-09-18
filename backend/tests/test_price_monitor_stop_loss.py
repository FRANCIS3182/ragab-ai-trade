from decimal import Decimal
from uuid import uuid4

from sqlalchemy import delete, select

from app.db.session import AsyncSessionLocal
from app.models.position import Position
from app.models.trading_account import TradingAccount
from app.models.user import User
from app.services.paper_market_data import PaperMarketDataProvider
from app.services.price_monitor import PriceMonitor


async def test_price_monitor_triggers_stop_loss():
    test_account_id = uuid4()

    provider = PaperMarketDataProvider()

    async with AsyncSessionLocal() as db:
        user_result = await db.execute(
            select(User).where(User.email == "ragabfrank1@gmail.com")
        )
        user = user_result.scalar_one()

        account = TradingAccount(
            id=test_account_id,
            name="PRICE_MONITOR_TEST",
            user_id=user.id,
            mode="paper",
            currency="USD",
            balance=Decimal("10000"),
            is_active=True,
        )
        db.add(account)
        await db.flush()

        position = Position(
            trading_account_id=account.id,
            symbol="XAUUSD",
            side="buy",
            quantity=Decimal("1"),
            entry_price=Decimal("3400"),
            current_price=Decimal("3400"),
            stop_loss=Decimal("3390"),
            unrealized_pnl=Decimal("0"),
            realized_pnl=Decimal("0"),
            status="open",
        )
        db.add(position)
        await db.flush()

        provider.set_price(
            "XAUUSD",
            Decimal("3390"),
            Decimal("3390"),
        )

        monitor = PriceMonitor(provider)

        updated = await monitor.run_once(db, account.id)

        await db.refresh(position)
        await db.refresh(account)

        assert updated == 1
        assert position.status == "closed"
        assert position.quantity == Decimal("0")
        assert position.realized_pnl == Decimal("-10")
        assert account.balance == Decimal("9990")

        await db.rollback()

    async with AsyncSessionLocal() as db:
        await db.execute(
            delete(Position).where(
                Position.trading_account_id == test_account_id
            )
        )
        await db.execute(
            delete(TradingAccount).where(
                TradingAccount.id == test_account_id
            )
        )
        await db.commit()

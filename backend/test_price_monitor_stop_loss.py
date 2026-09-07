import asyncio
from decimal import Decimal

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.position import Position
from app.models.trading_account import TradingAccount
from app.services.paper_market_data import PaperMarketDataProvider
from app.services.price_monitor import PriceMonitor


async def main():
    provider = PaperMarketDataProvider()

    async with AsyncSessionLocal() as db:
        account = TradingAccount(
            name="PRICE_MONITOR_TEST",
            user_id=__import__("uuid").UUID("f78bc625-ef85-428d-b5c0-ff69c929322a"),
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

        print("MONITOR_STOP_LOSS_TEST_OK")
        print("POSITION_STATUS:", position.status)
        print("POSITION_QUANTITY:", position.quantity)
        print("STOP_LOSS:", position.stop_loss)
        print("EXECUTION_PRICE:", position.current_price)
        print("REALIZED_PNL:", position.realized_pnl)
        print("ACCOUNT_BALANCE:", account.balance)

        await db.delete(account)
        await db.commit()

        print("TEST_ACCOUNT_CLEANED_UP")


asyncio.run(main())

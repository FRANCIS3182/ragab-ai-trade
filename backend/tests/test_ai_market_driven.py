from decimal import Decimal
from uuid import uuid4

from sqlalchemy import delete, select

from app.db.session import AsyncSessionLocal
from app.models.order import Order
from app.models.signal import Signal
from app.models.trading_account import TradingAccount
from app.models.user import User
from app.services.ai_trading import run_ai_market_driven_paper_trade
from app.services.paper_market_data import PaperMarketDataProvider


USER_EMAIL = "ragabfrank1@gmail.com"


async def test_ai_market_driven_paper_trade():
    test_account_id = uuid4()
    test_signal_id = None

    async with AsyncSessionLocal() as db:
        user_result = await db.execute(
            select(User).where(User.email == USER_EMAIL)
        )
        user = user_result.scalar_one()

        account = TradingAccount(
            id=test_account_id,
            user_id=user.id,
            name="AI Market Driven Test",
            mode="paper",
            currency="USD",
            balance=Decimal("10000"),
            is_active=True,
        )
        db.add(account)
        await db.flush()

        provider = PaperMarketDataProvider()

        for price in [
            Decimal("3390"),
            Decimal("3400"),
            Decimal("3410"),
        ]:
            provider.set_price("XAUUSD", price, price)

        result = await run_ai_market_driven_paper_trade(
            db=db,
            account=account,
            provider=provider,
            symbol="XAUUSD",
            timeframe="M5",
            period=3,
            quantity=Decimal("1"),
        )

        assert result.signal == "BUY"
        assert result.confidence == 0.60
        assert result.order_id is not None
        assert result.status == "paper_order_created"

        order_result = await db.execute(
            select(Order).where(
                Order.trading_account_id == test_account_id
            )
        )
        order = order_result.scalar_one()

        assert order.symbol == "XAUUSD"
        assert order.side == "buy"
        assert order.quantity == Decimal("1")
        assert order.price == Decimal("3410")
        assert order.status == "simulated"

        signal_result = await db.execute(
            select(Signal).where(
                Signal.symbol == "XAUUSD",
                Signal.timeframe == "M5",
            )
        )
        signal = signal_result.scalars().first()

        assert signal is not None
        test_signal_id = signal.id
        assert signal.direction == "BUY"

        await db.rollback()

    async with AsyncSessionLocal() as db:
        if test_signal_id is not None:
            await db.execute(
                delete(Signal).where(
                    Signal.id == test_signal_id
                )
            )

        await db.execute(
            delete(Order).where(
                Order.trading_account_id == test_account_id
            )
        )

        await db.execute(
            delete(TradingAccount).where(
                TradingAccount.id == test_account_id
            )
        )

        await db.commit()

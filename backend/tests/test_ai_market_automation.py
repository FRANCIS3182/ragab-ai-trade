from decimal import Decimal
from uuid import uuid4

from sqlalchemy import delete, select

from app.db.session import AsyncSessionLocal
from app.models.order import Order
from app.models.trading_account import TradingAccount
from app.models.user import User
from app.services.paper_market_data import PaperMarketDataProvider


async def test_ai_market_automation_market_history():
    test_account_id = uuid4()

    async with AsyncSessionLocal() as db:
        user_result = await db.execute(
            select(User).where(User.email == "ragabfrank1@gmail.com")
        )
        user = user_result.scalar_one()

        account = TradingAccount(
            id=test_account_id,
            user_id=user.id,
            name="AI Market Automation Test",
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
            Decimal("3410"),
            Decimal("3400"),
        ]:
            provider.set_price("XAUUSD", price, price)

        history = provider.get_price_history("XAUUSD")

        assert len(history) == 3
        assert history[-1].mid == Decimal("3400")

        await db.rollback()

    async with AsyncSessionLocal() as db:
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

import asyncio
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import delete, select

from app.db.session import AsyncSessionLocal
from app.models.order import Order
from app.models.signal import Signal
from app.models.trading_account import TradingAccount
from app.models.user import User
from app.services.paper_market_data import PaperMarketDataProvider


USER_EMAIL = "ragabfrank1@gmail.com"


async def main():
    async with AsyncSessionLocal() as db:
        user_result = await db.execute(
            select(User).where(User.email == USER_EMAIL)
        )
        user = user_result.scalar_one()

        account = TradingAccount(
            id=uuid4(),
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

        print("AI_MARKET_DATA_TEST_OK")
        print("HISTORY_COUNT:", len(history))
        print("LATEST_MID:", history[-1].mid)

        await db.rollback()

        await db.execute(
            delete(Order).where(
                Order.trading_account_id == account.id
            )
        )
        await db.execute(
            delete(TradingAccount).where(
                TradingAccount.id == account.id
            )
        )
        await db.commit()


if __name__ == "__main__":
    asyncio.run(main())

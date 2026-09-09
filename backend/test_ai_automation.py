import asyncio
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import delete, select

from app.ai.analyzer import analyze_market
from app.db.session import AsyncSessionLocal
from app.models.order import Order
from app.models.signal import Signal
from app.models.trading_account import TradingAccount
from app.models.user import User
from app.services.ai_trading import run_ai_paper_trade


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
            name="AI Automation Integration Test",
            mode="paper",
            currency="USD",
            balance=Decimal("10000"),
            is_active=True,
        )
        db.add(account)
        await db.flush()

        result = await run_ai_paper_trade(
            db=db,
            account=account,
            symbol="XAUUSD",
            timeframe="M5",
            price=Decimal("3400"),
            moving_average=Decimal("3395"),
            quantity=Decimal("1"),
        )

        assert result.signal == "BUY"
        assert result.confidence == 0.60
        assert result.order_id is not None
        assert result.status == "paper_order_created"

        order_result = await db.execute(
            select(Order).where(
                Order.trading_account_id == account.id
            )
        )
        order = order_result.scalar_one()

        assert order.symbol == "XAUUSD"
        assert order.side == "buy"
        assert order.quantity == Decimal("1")
        assert order.price == Decimal("3400")
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
        assert signal.confidence == Decimal("0.60")

        print("AI_AUTOMATION_INTEGRATION_TEST_OK")
        print(f"SIGNAL: {result.signal}")
        print(f"CONFIDENCE: {result.confidence}")
        print(f"ORDER_ID: {result.order_id}")
        print(f"ORDER_STATUS: {order.status}")

        await db.rollback()

    async with AsyncSessionLocal() as db:
        account_result = await db.execute(
            select(TradingAccount).where(
                TradingAccount.name == "AI Automation Integration Test"
            )
        )
        test_account = account_result.scalar_one_or_none()

        if test_account is not None:
            await db.execute(
                delete(Signal).where(
                    Signal.id == test_signal_id
                )
            )
            await db.execute(
                delete(Order).where(
                    Order.trading_account_id == test_account.id
                )
            )
            await db.execute(
                delete(TradingAccount).where(
                    TradingAccount.id == test_account.id
                )
            )
            await db.commit()


if __name__ == "__main__":
    asyncio.run(main())

from decimal import Decimal
from uuid import uuid4

from sqlalchemy import delete, select

from app.db.session import AsyncSessionLocal
from app.models.order import Order
from app.models.position import Position
from app.models.realized_pnl_event import RealizedPnlEvent
from app.models.trading_account import TradingAccount
from app.models.user import User
from app.services.ai_trading import run_ai_paper_trade
from app.services.position_service import update_position_price


USER_EMAIL = "ragabfrank1@gmail.com"


async def test_ai_paper_trade_creates_position_with_stop_loss_and_closes_it():
    test_account_id = uuid4()

    async with AsyncSessionLocal() as db:
        user_result = await db.execute(
            select(User).where(User.email == USER_EMAIL)
        )
        user = user_result.scalar_one()

        account = TradingAccount(
            id=test_account_id,
            user_id=user.id,
            name="AI Stop Loss Integration Test",
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
            stop_loss=Decimal("3390"),
        )

        assert result.signal == "BUY"
        assert result.order_id is not None
        assert result.status == "paper_order_created"

        position_result = await db.execute(
            select(Position).where(
                Position.trading_account_id == account.id,
                Position.symbol == "XAUUSD",
                Position.side == "buy",
            )
        )
        position = position_result.scalar_one()

        assert position.status == "open"
        assert position.quantity == Decimal("1")
        assert position.entry_price == Decimal("3400")
        assert position.current_price == Decimal("3400")
        assert position.stop_loss == Decimal("3390")

        await update_position_price(
            db=db,
            position=position,
            current_price=Decimal("3390"),
        )

        assert position.status == "closed"
        assert position.quantity == Decimal("0")
        assert position.current_price == Decimal("3390")
        assert position.realized_pnl == Decimal("-10")
        assert position.unrealized_pnl == Decimal("0")

        account_result = await db.execute(
            select(TradingAccount).where(
                TradingAccount.id == account.id
            )
        )
        updated_account = account_result.scalar_one()

        assert updated_account.balance == Decimal("9990")

        pnl_result = await db.execute(
            select(RealizedPnlEvent).where(
                RealizedPnlEvent.position_id == position.id
            )
        )
        pnl_event = pnl_result.scalar_one()

        assert pnl_event.trading_account_id == account.id
        assert pnl_event.realized_pnl == Decimal("-10")

        order_result = await db.execute(
            select(Order).where(
                Order.trading_account_id == account.id
            )
        )
        order = order_result.scalar_one()

        assert order.stop_loss == Decimal("3390")
        assert order.status == "simulated"

        await db.rollback()

    async with AsyncSessionLocal() as db:
        await db.execute(
            delete(RealizedPnlEvent).where(
                RealizedPnlEvent.trading_account_id == test_account_id
            )
        )
        await db.execute(
            delete(Position).where(
                Position.trading_account_id == test_account_id
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

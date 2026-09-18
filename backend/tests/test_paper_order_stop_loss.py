from decimal import Decimal
from uuid import uuid4

from sqlalchemy import delete, select

from app.api.v1.routes.paper_trading import create_paper_order
from app.db.session import AsyncSessionLocal
from app.models.position import Position
from app.models.trading_account import TradingAccount
from app.models.user import User
from app.schemas.order import PaperOrderCreate


USER_EMAIL = "ragabfrank1@gmail.com"


async def test_paper_order_creates_position_with_stop_loss():
    test_account_id = uuid4()

    async with AsyncSessionLocal() as db:
        user_result = await db.execute(
            select(User).where(User.email == USER_EMAIL)
        )
        user = user_result.scalar_one()

        account = TradingAccount(
            id=test_account_id,
            user_id=user.id,
            name="Position Stop Loss Integration Test",
            mode="paper",
            currency="USD",
            balance=Decimal("10000"),
            is_active=True,
        )
        db.add(account)
        await db.flush()

        payload = PaperOrderCreate(
            trading_account_id=account.id,
            symbol="XAUUSD",
            side="buy",
            quantity=Decimal("1"),
            price=Decimal("3400"),
            stop_loss=Decimal("3390"),
        )

        order = await create_paper_order(
            payload=payload,
            db=db,
            current_user=user,
        )

        assert order.stop_loss == Decimal("3390")

        position_result = await db.execute(
            select(Position).where(
                Position.trading_account_id == account.id,
                Position.status == "open",
            )
        )
        position = position_result.scalar_one()

        assert position.stop_loss == Decimal("3390")

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

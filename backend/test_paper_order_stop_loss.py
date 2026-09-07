import asyncio
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


async def main():
    async with AsyncSessionLocal() as db:
        user_result = await db.execute(
            select(User).where(User.email == USER_EMAIL)
        )
        user = user_result.scalar_one()

        account = TradingAccount(
            id=uuid4(),
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

        assert order.stop_loss == Decimal("3390"), order.stop_loss

        position_result = await db.execute(
            select(Position).where(
                Position.trading_account_id == account.id,
                Position.status == "open",
            )
        )
        position = position_result.scalar_one()

        assert position.stop_loss == Decimal("3390"), position.stop_loss

        print("PAPER_ORDER_STOP_LOSS_INTEGRATION_TEST_OK")
        print(f"ORDER STOP LOSS: {order.stop_loss}")
        print(f"POSITION STOP LOSS: {position.stop_loss}")

        await db.rollback()

    async with AsyncSessionLocal() as db:
        account_result = await db.execute(
            select(TradingAccount).where(
                TradingAccount.name == "Position Stop Loss Integration Test"
            )
        )
        test_account = account_result.scalar_one_or_none()

        if test_account is not None:
            await db.execute(
                delete(Position).where(
                    Position.trading_account_id == test_account.id
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

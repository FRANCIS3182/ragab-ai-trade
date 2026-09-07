import asyncio
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import delete, select

from app.db.session import AsyncSessionLocal
from app.models.position import Position
from app.models.trading_account import TradingAccount
from app.models.user import User
from app.services.position_service import close_position


async def main():
    async with AsyncSessionLocal() as db:
        user_result = await db.execute(
            select(User).where(User.email == "ragabfrank1@gmail.com")
        )
        user = user_result.scalar_one()

        account = TradingAccount(
            id=uuid4(),
            user_id=user.id,
            name="Stop Loss Execution Test",
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

        realized = await close_position(
            db=db,
            position=position,
            quantity=position.quantity,
            exit_price=Decimal("3390"),
        )

        assert realized == Decimal("-10"), realized
        assert position.status == "closed", position.status
        assert position.quantity == Decimal("0"), position.quantity
        assert position.closed_at is not None

        print("STOP_LOSS_EXECUTION_TEST_OK")
        print(f"REALIZED P/L: {realized}")
        print(f"POSITION STATUS: {position.status}")

        await db.rollback()

    async with AsyncSessionLocal() as db:
        account_result = await db.execute(
            select(TradingAccount).where(
                TradingAccount.name == "Stop Loss Execution Test"
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

import asyncio
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import delete, select

from app.db.session import AsyncSessionLocal
from app.models.position import Position
from app.models.realized_pnl_event import RealizedPnlEvent
from app.models.trading_account import TradingAccount
from app.models.user import User
from app.services.position_service import close_position
from app.services.risk_service import validate_paper_order_risk


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
            name="Daily Loss Integration Test",
            mode="paper",
            currency="USD",
            balance=Decimal("10000"),
            is_active=True,
        )
        db.add(account)
        await db.flush()

        losing_position = Position(
            id=uuid4(),
            trading_account_id=account.id,
            symbol="XAUUSD",
            side="buy",
            quantity=Decimal("20"),
            entry_price=Decimal("3400"),
            current_price=Decimal("3400"),
            unrealized_pnl=Decimal("0"),
            realized_pnl=Decimal("0"),
            status="open",
        )
        db.add(losing_position)
        await db.flush()

        realized = await close_position(
            db=db,
            position=losing_position,
            quantity=Decimal("10"),
            exit_price=Decimal("3370"),
        )
        await db.flush()

        assert realized == Decimal("-300"), realized
        assert losing_position.status == "open"
        assert losing_position.quantity == Decimal("10")
        assert losing_position.realized_pnl == Decimal("-300")

        try:
            await validate_paper_order_risk(
                db=db,
                trading_account_id=account.id,
                symbol="XAUUSD",
                side="buy",
                quantity=Decimal("1"),
                price=Decimal("3400"),
                stop_loss=Decimal("3390"),
            )
        except ValueError as exc:
            expected = "Daily loss limit reached"
            assert expected in str(exc), str(exc)
            print("DAILY_LOSS_INTEGRATION_TEST_OK")
            print(f"DAILY LOSS: $300.00")
            print("LIMIT: $300.00")
        else:
            raise AssertionError(
                "Order was accepted after the 3% daily loss limit was reached"
            )

        await db.rollback()

    async with AsyncSessionLocal() as db:
        account_result = await db.execute(
            select(TradingAccount).where(
                TradingAccount.name == "Daily Loss Integration Test"
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

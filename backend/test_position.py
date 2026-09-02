import asyncio
from decimal import Decimal

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.position import Position
from app.services.position_service import close_position


async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Position).where(
                Position.id == "9def79d0-cba7-40a9-b128-ddbce151d94c"
            )
        )
        position = result.scalar_one()

        await close_position(
            db,
            position,
            Decimal("0.005"),
            Decimal("3410"),
        )

        print("REMAINING QTY:", position.quantity)
        print("REALIZED P/L:", position.realized_pnl)
        print("STATUS:", position.status)
        print("UNREALIZED P/L:", position.unrealized_pnl)

        await db.rollback()


asyncio.run(main())

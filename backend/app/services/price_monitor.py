from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.position import Position
from app.services.market_data import MarketDataProvider
from app.services.position_service import update_position_price


class PriceMonitor:
    def __init__(
        self,
        provider: MarketDataProvider,
        interval_seconds: float = 1.0,
    ) -> None:
        self.provider = provider
        self.interval_seconds = interval_seconds

    async def update_open_positions(
        self,
        db: AsyncSession,
        trading_account_id: UUID,
    ) -> int:
        result = await db.execute(
            select(Position).where(
                Position.trading_account_id == trading_account_id,
                Position.status == "open",
                Position.quantity > 0,
            )
        )

        positions = result.scalars().all()
        updated = 0

        for position in positions:
            market_price = await self.provider.get_price(position.symbol)

            await update_position_price(
                db,
                position,
                market_price.mid,
            )

            updated += 1

        return updated

    async def run_once(
        self,
        db: AsyncSession,
        trading_account_id: UUID,
    ) -> int:
        updated = await self.update_open_positions(
            db,
            trading_account_id,
        )

        await db.commit()

        return updated

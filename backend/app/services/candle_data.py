from typing import Protocol

from app.services.market_candle import MarketCandle


class CandleDataProvider(Protocol):
    async def get_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
    ) -> list[MarketCandle]:
        ...

from decimal import Decimal

from app.services.market_data import MarketDataProvider, MarketPrice


class PaperMarketDataProvider:
    def __init__(self) -> None:
        self._prices: dict[str, MarketPrice] = {}

    def set_price(
        self,
        symbol: str,
        bid: Decimal,
        ask: Decimal,
    ) -> None:
        from datetime import datetime, timezone

        self._prices[symbol] = MarketPrice(
            symbol=symbol,
            bid=bid,
            ask=ask,
            timestamp=datetime.now(timezone.utc),
        )

    async def get_price(self, symbol: str) -> MarketPrice:
        price = self._prices.get(symbol)

        if price is None:
            raise ValueError(f"No paper market price available for {symbol}")

        return price

from decimal import Decimal

from app.services.market_data import MarketDataProvider, MarketPrice


class PaperMarketDataProvider:
    def __init__(self) -> None:
        self._prices: dict[str, MarketPrice] = {}
        self._history: dict[str, list[MarketPrice]] = {}

    def set_price(
        self,
        symbol: str,
        bid: Decimal,
        ask: Decimal,
    ) -> None:
        from datetime import datetime, timezone

        market_price = MarketPrice(
            symbol=symbol,
            bid=bid,
            ask=ask,
            timestamp=datetime.now(timezone.utc),
        )

        normalized_symbol = symbol.upper()

        self._prices[normalized_symbol] = market_price
        self._history.setdefault(normalized_symbol, []).append(market_price)

    async def get_price(self, symbol: str) -> MarketPrice:
        price = self._prices.get(symbol.upper())

        if price is None:
            raise ValueError(f"No paper market price available for {symbol}")

        return price

    def get_price_history(self, symbol: str) -> list[MarketPrice]:
        return list(self._history.get(symbol.upper(), []))

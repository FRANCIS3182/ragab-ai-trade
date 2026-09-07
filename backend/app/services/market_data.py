from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class MarketPrice:
    symbol: str
    bid: Decimal
    ask: Decimal
    timestamp: datetime

    @property
    def mid(self) -> Decimal:
        return (self.bid + self.ask) / Decimal("2")


class MarketDataProvider(Protocol):
    async def get_price(self, symbol: str) -> MarketPrice:
        ...

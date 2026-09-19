from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class MarketCandle:
    symbol: str
    timeframe: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal | None = None

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("symbol cannot be empty")

        if not self.timeframe.strip():
            raise ValueError("timeframe cannot be empty")

        if self.open <= 0:
            raise ValueError("open must be greater than zero")

        if self.high <= 0:
            raise ValueError("high must be greater than zero")

        if self.low <= 0:
            raise ValueError("low must be greater than zero")

        if self.close <= 0:
            raise ValueError("close must be greater than zero")

        if self.high < self.low:
            raise ValueError("high cannot be below low")

        if self.open < self.low or self.open > self.high:
            raise ValueError("open must be between low and high")

        if self.close < self.low or self.close > self.high:
            raise ValueError("close must be between low and high")

        if self.volume is not None and self.volume < 0:
            raise ValueError("volume cannot be negative")

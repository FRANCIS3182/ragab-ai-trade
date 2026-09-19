from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import httpx

from app.services.candle_data import CandleDataProvider
from app.services.market_candle import MarketCandle
from app.services.timeframes import normalize_timeframe


class TwelveDataCandleProvider:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.twelvedata.com",
        timeout_seconds: float = 10.0,
    ) -> None:
        if not api_key:
            raise ValueError("Twelve Data API key is required")

        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def get_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
    ) -> list[MarketCandle]:
        if limit <= 0:
            raise ValueError("limit must be greater than zero")

        interval = normalize_timeframe(timeframe)

        data = await self._request(
            "/time_series",
            {
                "symbol": self._normalize_symbol(symbol),
                "interval": interval,
                "outputsize": limit,
                "apikey": self.api_key,
            },
        )

        values = data.get("values")

        if not isinstance(values, list):
            raise ValueError("Twelve Data returned no candle values")

        candles: list[MarketCandle] = []

        for item in reversed(values):
            candles.append(self._parse_candle(item, symbol, timeframe))

        return candles

    async def _request(
        self,
        path: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"

        async with httpx.AsyncClient(
            timeout=self.timeout_seconds
        ) as client:
            response = await client.get(url, params=params)

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict):
            raise ValueError("Twelve Data returned an invalid response")

        if data.get("status") == "error":
            message = data.get("message", "Unknown Twelve Data error")
            raise ValueError(f"Twelve Data error: {message}")

        return data

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        normalized = symbol.strip().upper()

        if normalized == "XAUUSD":
            return "XAU/USD"

        return normalized

    @staticmethod
    def _parse_candle(
        item: dict[str, Any],
        symbol: str,
        timeframe: str,
    ) -> MarketCandle:
        try:
            timestamp = datetime.fromisoformat(
                str(item["datetime"]).replace("Z", "+00:00")
            )

            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)

            return MarketCandle(
                symbol=symbol.upper(),
                timeframe=timeframe.upper(),
                timestamp=timestamp,
                open=Decimal(str(item["open"])),
                high=Decimal(str(item["high"])),
                low=Decimal(str(item["low"])),
                close=Decimal(str(item["close"])),
                volume=(
                    Decimal(str(item["volume"]))
                    if item.get("volume") is not None
                    else None
                ),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                "Invalid candle returned by Twelve Data"
            ) from exc

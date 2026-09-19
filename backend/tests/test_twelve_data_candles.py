from decimal import Decimal

import httpx
import pytest

from app.services.twelve_data_candles import TwelveDataCandleProvider


@pytest.mark.asyncio
async def test_get_candles_parses_and_orders_data(monkeypatch):
    provider = TwelveDataCandleProvider(
        api_key="test-key",
        base_url="https://example.test",
    )

    async def mock_request(self, path, params):
        assert path == "/time_series"
        assert params["symbol"] == "XAU/USD"
        assert params["interval"] == "5min"
        assert params["outputsize"] == 3
        assert params["apikey"] == "test-key"

        return {
            "meta": {"symbol": "XAU/USD"},
            "values": [
                {
                    "datetime": "2026-09-20 01:10:00",
                    "open": "3410.00",
                    "high": "3415.00",
                    "low": "3408.00",
                    "close": "3412.00",
                    "volume": "100",
                },
                {
                    "datetime": "2026-09-20 01:05:00",
                    "open": "3405.00",
                    "high": "3411.00",
                    "low": "3403.00",
                    "close": "3410.00",
                    "volume": "90",
                },
                {
                    "datetime": "2026-09-20 01:00:00",
                    "open": "3400.00",
                    "high": "3407.00",
                    "low": "3398.00",
                    "close": "3405.00",
                    "volume": "80",
                },
            ],
        }

    monkeypatch.setattr(
        TwelveDataCandleProvider,
        "_request",
        mock_request,
    )

    candles = await provider.get_candles(
        symbol="XAUUSD",
        timeframe="M5",
        limit=3,
    )

    assert len(candles) == 3
    assert candles[0].close == Decimal("3405.00")
    assert candles[1].close == Decimal("3410.00")
    assert candles[2].close == Decimal("3412.00")
    assert candles[0].open == Decimal("3400.00")
    assert candles[2].high == Decimal("3415.00")


@pytest.mark.asyncio
async def test_get_candles_rejects_invalid_limit():
    provider = TwelveDataCandleProvider(api_key="test-key")

    with pytest.raises(ValueError, match="limit"):
        await provider.get_candles(
            symbol="XAUUSD",
            timeframe="M5",
            limit=0,
        )


@pytest.mark.asyncio
async def test_get_candles_rejects_invalid_timeframe():
    provider = TwelveDataCandleProvider(api_key="test-key")

    with pytest.raises(ValueError, match="Unsupported timeframe"):
        await provider.get_candles(
            symbol="XAUUSD",
            timeframe="M2",
            limit=10,
        )


@pytest.mark.asyncio
async def test_provider_requires_api_key():
    with pytest.raises(ValueError, match="API key"):
        TwelveDataCandleProvider(api_key="")


@pytest.mark.asyncio
async def test_request_raises_for_http_error(monkeypatch):
    provider = TwelveDataCandleProvider(
        api_key="test-key",
        base_url="https://example.test",
    )

    class MockResponse:
        def raise_for_status(self):
            raise httpx.HTTPStatusError(
                "server error",
                request=httpx.Request("GET", "https://example.test"),
                response=httpx.Response(500),
            )

        def json(self):
            return {}

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, params):
            return MockResponse()

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: MockClient(),
    )

    with pytest.raises(httpx.HTTPStatusError):
        await provider._request(
            "/time_series",
            {"symbol": "XAU/USD"},
        )


@pytest.mark.asyncio
async def test_request_raises_for_api_error(monkeypatch):
    provider = TwelveDataCandleProvider(
        api_key="test-key",
        base_url="https://example.test",
    )

    class MockResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "status": "error",
                "message": "Invalid API key",
            }

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, params):
            return MockResponse()

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: MockClient(),
    )

    with pytest.raises(ValueError, match="Invalid API key"):
        await provider._request(
            "/time_series",
            {"symbol": "XAU/USD"},
        )

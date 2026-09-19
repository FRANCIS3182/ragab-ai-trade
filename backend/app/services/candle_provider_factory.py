from app.core.config import settings
from app.services.candle_data import CandleDataProvider
from app.services.twelve_data_candles import TwelveDataCandleProvider


def create_twelve_data_provider() -> CandleDataProvider:
    if not settings.twelve_data_api_key:
        raise ValueError(
            "Twelve Data API key is not configured"
        )

    return TwelveDataCandleProvider(
        api_key=settings.twelve_data_api_key,
        base_url=settings.twelve_data_base_url,
    )

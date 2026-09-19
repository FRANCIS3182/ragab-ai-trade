TIMEFRAME_MAP = {
    "M1": "1min",
    "M5": "5min",
    "M15": "15min",
    "M30": "30min",
    "H1": "1h",
    "H4": "4h",
    "D1": "1day",
}


def normalize_timeframe(timeframe: str) -> str:
    normalized = timeframe.strip().upper()

    try:
        return TIMEFRAME_MAP[normalized]
    except KeyError as exc:
        supported = ", ".join(TIMEFRAME_MAP)
        raise ValueError(
            f"Unsupported timeframe {timeframe!r}. "
            f"Supported timeframes: {supported}"
        ) from exc

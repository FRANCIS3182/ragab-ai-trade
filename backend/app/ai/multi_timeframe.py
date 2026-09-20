from typing import Literal


TrendSignal = Literal["UP", "DOWN", "SIDEWAYS"]


def analyze_multi_timeframe(
    signals: dict[str, TrendSignal],
) -> TrendSignal:
    if not signals:
        raise ValueError("at least one timeframe signal is required")

    up_count = sum(signal == "UP" for signal in signals.values())
    down_count = sum(signal == "DOWN" for signal in signals.values())

    if up_count > down_count:
        return "UP"

    if down_count > up_count:
        return "DOWN"

    return "SIDEWAYS"

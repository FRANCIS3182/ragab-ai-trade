import pytest

from app.ai.multi_timeframe import analyze_multi_timeframe


def test_multi_timeframe_up():
    assert analyze_multi_timeframe(
        {
            "H4": "UP",
            "H1": "UP",
            "M15": "DOWN",
        }
    ) == "UP"


def test_multi_timeframe_down():
    assert analyze_multi_timeframe(
        {
            "H4": "DOWN",
            "H1": "DOWN",
            "M15": "UP",
        }
    ) == "DOWN"


def test_multi_timeframe_sideways_on_tie():
    assert analyze_multi_timeframe(
        {
            "H4": "UP",
            "H1": "DOWN",
        }
    ) == "SIDEWAYS"


def test_multi_timeframe_sideways_only():
    assert analyze_multi_timeframe(
        {
            "H4": "SIDEWAYS",
            "H1": "SIDEWAYS",
            "M15": "SIDEWAYS",
        }
    ) == "SIDEWAYS"


def test_multi_timeframe_requires_signal():
    with pytest.raises(
        ValueError,
        match="at least one timeframe signal",
    ):
        analyze_multi_timeframe({})

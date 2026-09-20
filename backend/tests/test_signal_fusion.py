from app.ai.signal_fusion import fuse_signals


def test_signal_fusion_buy():
    result = fuse_signals(
        trend="UP",
        volatility="LOW",
        support_resistance="SUPPORT",
        timeframe_signal="UP",
    )

    assert result.signal == "BUY"
    assert result.confidence == 1.0


def test_signal_fusion_sell():
    result = fuse_signals(
        trend="DOWN",
        volatility="LOW",
        support_resistance="RESISTANCE",
        timeframe_signal="DOWN",
    )

    assert result.signal == "SELL"
    assert result.confidence == 1.0


def test_signal_fusion_hold_on_balanced_score():
    result = fuse_signals(
        trend="UP",
        volatility="LOW",
        support_resistance="RESISTANCE",
        timeframe_signal="SIDEWAYS",
    )

    assert result.signal == "HOLD"
    assert result.confidence == 0.0


def test_high_volatility_reduces_confidence():
    result = fuse_signals(
        trend="UP",
        volatility="HIGH",
        support_resistance="SUPPORT",
        timeframe_signal="UP",
    )

    assert result.signal == "BUY"
    assert result.confidence == 0.75


def test_medium_volatility_reduces_confidence():
    result = fuse_signals(
        trend="UP",
        volatility="MEDIUM",
        support_resistance="SUPPORT",
        timeframe_signal="UP",
    )

    assert result.signal == "BUY"
    assert result.confidence == 0.9

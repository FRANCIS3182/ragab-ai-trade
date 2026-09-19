from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.analyzer import MarketAnalysis, analyze_market
from app.core.config import settings
from app.models.signal import Signal
from app.models.trading_account import TradingAccount
from app.services.paper_execution import execute_paper_order


@dataclass
class AutomationResult:
    signal: str
    confidence: float
    reason: str
    order_id: str | None
    status: str


async def run_ai_paper_trade(
    db: AsyncSession,
    account: TradingAccount,
    symbol: str,
    timeframe: str,
    price: Decimal,
    moving_average: Decimal,
    quantity: Decimal,
    stop_loss: Decimal | None = None,
) -> AutomationResult:
    analysis = analyze_market(
        symbol=symbol,
        timeframe=timeframe,
        price=float(price),
        moving_average=float(moving_average),
    )

    return await _execute_ai_analysis(
        db=db,
        account=account,
        symbol=symbol,
        timeframe=timeframe,
        price=price,
        analysis=analysis,
        quantity=quantity,
        stop_loss=stop_loss,
    )


async def _execute_ai_analysis(
    db: AsyncSession,
    account: TradingAccount,
    symbol: str,
    timeframe: str,
    price: Decimal,
    analysis: MarketAnalysis,
    quantity: Decimal,
    stop_loss: Decimal | None = None,
) -> AutomationResult:
    if not settings.paper_trading_only:
        raise ValueError("Paper trading safety flag must be enabled")

    signal = Signal(
        symbol=symbol.upper(),
        timeframe=timeframe,
        direction=analysis.signal,
        confidence=Decimal(str(analysis.confidence)),
        rationale=analysis.reason,
    )

    db.add(signal)

    if analysis.signal == "HOLD":
        await db.commit()

        return AutomationResult(
            signal=analysis.signal,
            confidence=analysis.confidence,
            reason=analysis.reason,
            order_id=None,
            status="no_trade",
        )

    try:
        order = await execute_paper_order(
            db=db,
            account=account,
            symbol=symbol,
            side=analysis.signal.lower(),
            quantity=quantity,
            price=price,
            stop_loss=stop_loss,
        )
    except ValueError:
        await db.rollback()
        raise

    return AutomationResult(
        signal=analysis.signal,
        confidence=analysis.confidence,
        reason=analysis.reason,
        order_id=str(order.id),
        status="paper_order_created",
    )


async def analyze_ai_market_signal(
    provider,
    symbol: str,
    timeframe: str,
    period: int,
):
    from app.ai.analyzer import analyze_market_history

    await provider.get_price(symbol)
    history = provider.get_price_history(symbol)

    return analyze_market_history(
        symbol=symbol,
        timeframe=timeframe,
        prices=history,
        period=period,
    )


async def run_ai_market_driven_paper_trade(
    db: AsyncSession,
    account: TradingAccount,
    provider,
    symbol: str,
    timeframe: str,
    period: int,
    quantity: Decimal,
    stop_loss: Decimal | None = None,
) -> AutomationResult:
    from app.ai.analyzer import analyze_market_history

    price = await provider.get_price(symbol)
    history = provider.get_price_history(symbol)

    analysis = analyze_market_history(
        symbol=symbol,
        timeframe=timeframe,
        prices=history,
        period=period,
    )

    return await _execute_ai_analysis(
        db=db,
        account=account,
        symbol=symbol,
        timeframe=timeframe,
        price=price.mid,
        analysis=analysis,
        quantity=quantity,
        stop_loss=stop_loss,
    )

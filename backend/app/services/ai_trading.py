from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.analyzer import MarketAnalysis, analyze_market
from app.core.config import settings
from app.models.order import Order
from app.models.risk_setting import RiskSetting
from app.models.signal import Signal
from app.models.trading_account import TradingAccount


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
    )


async def _execute_ai_analysis(
    db: AsyncSession,
    account: TradingAccount,
    symbol: str,
    timeframe: str,
    price: Decimal,
    analysis: MarketAnalysis,
    quantity: Decimal,
) -> AutomationResult:
    if not settings.paper_trading_only:
        raise ValueError("Paper trading safety flag must be enabled")

    risk_result = await db.execute(
        select(RiskSetting).where(
            RiskSetting.trading_account_id == account.id
        )
    )

    risk = risk_result.scalar_one_or_none()

    if risk is None:
        risk = RiskSetting(trading_account_id=account.id)
        db.add(risk)
        await db.flush()

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

    open_positions_result = await db.execute(
        select(func.count(Order.id)).where(
            Order.trading_account_id == account.id,
            Order.status == "simulated",
        )
    )

    open_positions = open_positions_result.scalar() or 0

    if open_positions >= risk.max_open_positions:
        await db.commit()

        return AutomationResult(
            signal=analysis.signal,
            confidence=analysis.confidence,
            reason="Maximum open paper positions reached.",
            order_id=None,
            status="risk_blocked",
        )

    order = Order(
        trading_account_id=account.id,
        symbol=symbol.upper(),
        side=analysis.signal.lower(),
        quantity=quantity,
        price=price,
        status="simulated",
    )

    db.add(order)

    await db.commit()
    await db.refresh(order)

    return AutomationResult(
        signal=analysis.signal,
        confidence=analysis.confidence,
        reason=analysis.reason,
        order_id=str(order.id),
        status="paper_order_created",
    )


async def run_ai_market_driven_paper_trade(
    db: AsyncSession,
    account: TradingAccount,
    provider,
    symbol: str,
    timeframe: str,
    period: int,
    quantity: Decimal,
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
    )

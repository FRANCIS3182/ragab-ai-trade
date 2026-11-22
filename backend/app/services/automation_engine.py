"""
Continuous Automation Engine

Runs AI market analysis on a schedule for configured symbols/accounts.
Paper-trading only. Designed to be started from FastAPI lifespan.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.trading_account import TradingAccount
from app.services.ai_trading import run_ai_market_driven_paper_trade

logger = logging.getLogger("automation_engine")


@dataclass
class AutomationJob:
    trading_account_id: UUID
    symbol: str
    timeframe: str = "15m"
    period: int = 20
    interval_seconds: int = 300  # 5 minutes default
    enabled: bool = True
    last_run: datetime | None = None
    last_result: dict[str, Any] | None = None
    run_count: int = 0
    error_count: int = 0


@dataclass
class AutomationEngine:
    session_factory: async_sessionmaker[AsyncSession]
    paper_market_data: Any
    jobs: dict[str, AutomationJob] = field(default_factory=dict)
    _task: asyncio.Task | None = None
    _running: bool = False
    min_confidence: float = 0.55

    def add_job(
        self,
        trading_account_id: UUID,
        symbol: str,
        timeframe: str = "15m",
        period: int = 20,
        interval_seconds: int = 300,
    ) -> str:
        key = f"{trading_account_id}:{symbol.upper()}:{timeframe}"
        self.jobs[key] = AutomationJob(
            trading_account_id=trading_account_id,
            symbol=symbol.upper(),
            timeframe=timeframe,
            period=period,
            interval_seconds=interval_seconds,
        )
        logger.info("Added automation job: %s", key)
        return key

    def remove_job(self, key: str) -> bool:
        if key in self.jobs:
            del self.jobs[key]
            logger.info("Removed automation job: %s", key)
            return True
        return False

    def enable_job(self, key: str) -> bool:
        job = self.jobs.get(key)
        if job:
            job.enabled = True
            return True
        return False

    def disable_job(self, key: str) -> bool:
        job = self.jobs.get(key)
        if job:
            job.enabled = False
            return True
        return False

    def list_jobs(self) -> list[dict[str, Any]]:
        result = []
        for key, job in self.jobs.items():
            result.append(
                {
                    "key": key,
                    "trading_account_id": str(job.trading_account_id),
                    "symbol": job.symbol,
                    "timeframe": job.timeframe,
                    "period": job.period,
                    "interval_seconds": job.interval_seconds,
                    "enabled": job.enabled,
                    "last_run": job.last_run.isoformat() if job.last_run else None,
                    "last_result": job.last_result,
                    "run_count": job.run_count,
                    "error_count": job.error_count,
                }
            )
        return result

    async def _run_single_job(self, key: str, job: AutomationJob) -> None:
        now = datetime.now(timezone.utc)

        if job.last_run and (now - job.last_run).total_seconds() < job.interval_seconds:
            return

        async with self.session_factory() as db:
            result = await db.execute(
                select(TradingAccount).where(
                    TradingAccount.id == job.trading_account_id,
                    TradingAccount.is_active.is_(True),
                    TradingAccount.mode == "paper",
                )
            )
            account = result.scalar_one_or_none()

            if not account:
                logger.warning("Account %s not found or inactive", job.trading_account_id)
                job.error_count += 1
                job.last_result = {"error": "account_not_found_or_inactive"}
                job.last_run = now
                return

            try:
                automation = await run_ai_market_driven_paper_trade(
                    db=db,
                    account=account,
                    provider=self.paper_market_data,
                    symbol=job.symbol,
                    timeframe=job.timeframe,
                    period=job.period,
                )

                job.run_count += 1
                job.last_run = now
                job.last_result = {
                    "signal": automation.signal,
                    "confidence": automation.confidence,
                    "reason": automation.reason,
                    "status": automation.status,
                    "order_id": automation.order_id,
                    "quantity": str(automation.quantity) if automation.quantity else None,
                    "stop_loss": str(automation.stop_loss) if automation.stop_loss else None,
                    "rsi": automation.rsi,
                    "trend": automation.trend,
                    "timestamp": now.isoformat(),
                }

                if automation.status == "paper_order_created":
                    logger.info(
                        "Trade executed | %s | %s | conf=%.2f | qty=%s",
                        job.symbol,
                        automation.signal,
                        automation.confidence,
                        automation.quantity,
                    )
                else:
                    logger.info(
                        "No trade | %s | %s | conf=%.2f | %s",
                        job.symbol,
                        automation.signal,
                        automation.confidence,
                        automation.status,
                    )

            except Exception as exc:
                job.error_count += 1
                job.last_run = now
                job.last_result = {"error": str(exc), "timestamp": now.isoformat()}
                logger.exception("Automation job failed: %s", key)

    async def _loop(self) -> None:
        logger.info("Automation engine started")
        while self._running:
            try:
                for key, job in list(self.jobs.items()):
                    if job.enabled:
                        await self._run_single_job(key, job)
            except Exception:
                logger.exception("Unexpected error in automation loop")

            await asyncio.sleep(15)  # check every 15 seconds which jobs are due

        logger.info("Automation engine stopped")

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

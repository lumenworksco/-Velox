"""Portfolio API endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class PortfolioSummary(BaseModel):
    """Portfolio overview"""
    total_value: float
    cash: float
    equity_value: float
    day_pnl: float
    day_pnl_percent: float
    total_pnl: float
    total_pnl_percent: float
    buying_power: float


class PerformanceMetrics(BaseModel):
    """Portfolio performance metrics"""
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    avg_win: float
    avg_loss: float
    profit_factor: float


@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary():
    """
    Get portfolio summary and key metrics.

    Returns total value, P&L, and buying power.
    """
    try:
        # Mock data - integrate with real portfolio manager
        return PortfolioSummary(
            total_value=105000.00,
            cash=50000.00,
            equity_value=55000.00,
            day_pnl=1250.00,
            day_pnl_percent=1.20,
            total_pnl=5000.00,
            total_pnl_percent=5.00,
            buying_power=200000.00
        )

    except Exception as e:
        logger.error(f"Error fetching portfolio summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics():
    """
    Get portfolio performance analytics.

    Returns Sharpe ratio, max drawdown, win rate, etc.
    """
    try:
        # Mock data - calculate from actual trade history
        return PerformanceMetrics(
            sharpe_ratio=1.85,
            max_drawdown=8.5,
            win_rate=62.5,
            total_trades=48,
            avg_win=850.00,
            avg_loss=420.00,
            profit_factor=2.02
        )

    except Exception as e:
        logger.error(f"Error fetching performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_equity_history(days: int = 30):
    """
    Get portfolio equity curve history.

    Returns daily equity values for charting.
    """
    try:
        # Mock equity curve data
        # In production, query from database
        import pandas as pd
        import numpy as np

        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        # Simulate equity curve with growth + noise
        equity = 100000 * (1 + np.linspace(0, 0.05, days) + np.random.randn(days) * 0.01)

        return [
            {
                "date": date.isoformat(),
                "equity": float(value)
            }
            for date, value in zip(dates, equity)
        ]

    except Exception as e:
        logger.error(f"Error fetching equity history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

"""Portfolio API endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
import logging
import os

from core.config import ALPACA_AVAILABLE
if ALPACA_AVAILABLE:
    from alpaca_trade_api import REST

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Alpaca API client
alpaca_api = None
if ALPACA_AVAILABLE:
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    paper = os.getenv('ALPACA_PAPER', 'true').lower() == 'true'

    if api_key and secret_key:
        try:
            base_url = 'https://paper-api.alpaca.markets' if paper else 'https://api.alpaca.markets'
            alpaca_api = REST(api_key, secret_key, base_url, api_version='v2')
            logger.info(f"Connected to Alpaca {'Paper' if paper else 'Live'} Trading")
        except Exception as e:
            logger.error(f"Failed to connect to Alpaca: {e}")


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
        if alpaca_api:
            # Get real account data from Alpaca
            account = alpaca_api.get_account()

            total_value = float(account.portfolio_value)
            cash = float(account.cash)
            equity_value = float(account.equity) if hasattr(account, 'equity') else (total_value - cash)

            # Calculate initial equity (this would ideally be stored in a database)
            # For now, use a conservative estimate
            initial_equity = 100000.00  # This should be tracked in database

            total_pnl = total_value - initial_equity
            total_pnl_percent = (total_pnl / initial_equity * 100) if initial_equity > 0 else 0

            # Get today's P&L if available
            try:
                day_pnl = float(account.equity) - float(account.last_equity) if hasattr(account, 'last_equity') else 0
                day_pnl_percent = (day_pnl / float(account.last_equity) * 100) if hasattr(account, 'last_equity') and float(account.last_equity) > 0 else 0
            except:
                day_pnl = 0
                day_pnl_percent = 0

            buying_power = float(account.buying_power)

            return PortfolioSummary(
                total_value=total_value,
                cash=cash,
                equity_value=equity_value,
                day_pnl=day_pnl,
                day_pnl_percent=day_pnl_percent,
                total_pnl=total_pnl,
                total_pnl_percent=total_pnl_percent,
                buying_power=buying_power
            )
        else:
            # Fallback to mock data if Alpaca not available
            return PortfolioSummary(
                total_value=100000.00,
                cash=100000.00,
                equity_value=0.00,
                day_pnl=0.00,
                day_pnl_percent=0.00,
                total_pnl=0.00,
                total_pnl_percent=0.00,
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
        if alpaca_api:
            # Get actual trading activity from Alpaca
            try:
                import pandas as pd
                from datetime import datetime, timedelta

                # Get closed orders (filled trades) from the last 90 days
                end_date = datetime.now()
                start_date = end_date - timedelta(days=90)

                orders = alpaca_api.list_orders(
                    status='closed',
                    limit=500,
                    after=start_date.isoformat()
                )

                # Filter for filled orders only
                filled_orders = [o for o in orders if o.filled_at is not None]

                if len(filled_orders) == 0:
                    # No trades yet - return zeros
                    return PerformanceMetrics(
                        sharpe_ratio=0.0,
                        max_drawdown=0.0,
                        win_rate=0.0,
                        total_trades=0,
                        avg_win=0.0,
                        avg_loss=0.0,
                        profit_factor=0.0
                    )

                # Calculate basic trade statistics
                # Note: For full P&L calculation, we'd need to match buy/sell pairs
                # For now, just show trade counts
                total_trades = len(filled_orders)

                # Get portfolio history for performance calculations
                portfolio_history = alpaca_api.get_portfolio_history(
                    period='3M',
                    timeframe='1D'
                )

                if portfolio_history and hasattr(portfolio_history, 'equity'):
                    equity_values = portfolio_history.equity

                    # Calculate returns
                    returns = pd.Series(equity_values).pct_change().dropna()

                    # Sharpe ratio (annualized, assuming risk-free rate = 0)
                    if len(returns) > 1 and returns.std() > 0:
                        sharpe_ratio = (returns.mean() / returns.std()) * (252 ** 0.5)
                    else:
                        sharpe_ratio = 0.0

                    # Max drawdown
                    cumulative = (1 + returns).cumprod()
                    running_max = cumulative.expanding().max()
                    drawdown = (cumulative - running_max) / running_max
                    max_drawdown = abs(drawdown.min() * 100)
                else:
                    sharpe_ratio = 0.0
                    max_drawdown = 0.0

                # Since we can't easily calculate win/loss without position tracking,
                # return basic metrics
                return PerformanceMetrics(
                    sharpe_ratio=round(sharpe_ratio, 2),
                    max_drawdown=round(max_drawdown, 2),
                    win_rate=0.0,  # Would need position tracking
                    total_trades=total_trades,
                    avg_win=0.0,  # Would need position tracking
                    avg_loss=0.0,  # Would need position tracking
                    profit_factor=0.0  # Would need position tracking
                )

            except Exception as e:
                logger.warning(f"Could not calculate performance metrics: {e}")
                # Return zeros instead of mock data
                return PerformanceMetrics(
                    sharpe_ratio=0.0,
                    max_drawdown=0.0,
                    win_rate=0.0,
                    total_trades=0,
                    avg_win=0.0,
                    avg_loss=0.0,
                    profit_factor=0.0
                )
        else:
            # No Alpaca connection - return zeros
            return PerformanceMetrics(
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                win_rate=0.0,
                total_trades=0,
                avg_win=0.0,
                avg_loss=0.0,
                profit_factor=0.0
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
        if alpaca_api:
            # Try to get real portfolio history from Alpaca
            try:
                account = alpaca_api.get_account()
                current_value = float(account.portfolio_value)

                # Get actual portfolio history if available
                import pandas as pd
                from datetime import datetime, timedelta

                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)

                # Alpaca portfolio history endpoint
                portfolio_history = alpaca_api.get_portfolio_history(
                    period=f'{days}D',
                    timeframe='1D'
                )

                if portfolio_history and hasattr(portfolio_history, 'equity'):
                    dates = [datetime.fromtimestamp(ts) for ts in portfolio_history.timestamp]
                    return [
                        {
                            "date": date.isoformat(),
                            "equity": float(value)
                        }
                        for date, value in zip(dates, portfolio_history.equity)
                    ]
            except Exception as e:
                logger.warning(f"Could not fetch real portfolio history: {e}")

        # Fallback: Generate realistic mock data based on current account value
        import pandas as pd
        import numpy as np

        # Get current value or use default
        try:
            if alpaca_api:
                account = alpaca_api.get_account()
                current_value = float(account.portfolio_value)
            else:
                current_value = 100000.0
        except:
            current_value = 100000.0

        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        # Simulate equity curve ending at current value with realistic volatility
        daily_return = -0.0005  # Slight downward trend to match current value
        equity = current_value * np.exp(daily_return * np.arange(days-1, -1, -1) + np.cumsum(np.random.randn(days) * 0.01))

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

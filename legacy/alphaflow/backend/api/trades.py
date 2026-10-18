"""Trade history API endpoints"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from backend.trade_history import trade_history, Trade

logger = logging.getLogger(__name__)
router = APIRouter()


class TradeResponse(BaseModel):
    """Trade response model"""
    trade_id: str
    timestamp: str
    strategy_id: str
    symbol: str
    side: str
    shares: float
    price: float
    order_type: str
    status: str
    commission: float
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    entry_price: Optional[float] = None
    hold_duration: Optional[str] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    notes: Optional[str] = None
    alpaca_order_id: Optional[str] = None


class PerformanceStatsResponse(BaseModel):
    """Performance statistics response"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    avg_pnl: float
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    profit_factor: float


@router.get("/history", response_model=List[TradeResponse])
async def get_trade_history(
    limit: int = Query(50, ge=1, le=1000),
    strategy_id: Optional[str] = None,
    symbol: Optional[str] = None
):
    """
    Get trade history with optional filters

    Args:
        limit: Maximum number of trades to return
        strategy_id: Filter by strategy
        symbol: Filter by symbol

    Returns:
        List of trades
    """
    try:
        if strategy_id:
            trades = trade_history.get_trades_by_strategy(strategy_id)
        elif symbol:
            trades = trade_history.get_trades_by_symbol(symbol)
        else:
            trades = trade_history.get_recent_trades(limit)

        return trades[-limit:]  # Return most recent
    except Exception as e:
        logger.error(f"Error fetching trade history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/all", response_model=List[TradeResponse])
async def get_all_trades():
    """Get all trade history"""
    try:
        trades = trade_history.get_all_trades()
        return trades
    except Exception as e:
        logger.error(f"Error fetching all trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/date-range", response_model=List[TradeResponse])
async def get_trades_by_date_range(
    start_date: str,
    end_date: str
):
    """
    Get trades within a date range

    Args:
        start_date: Start date (ISO format: 2026-01-01T00:00:00)
        end_date: End date (ISO format: 2026-01-31T23:59:59)

    Returns:
        List of trades within the date range
    """
    try:
        trades = trade_history.get_trades_by_date_range(start_date, end_date)
        return trades
    except Exception as e:
        logger.error(f"Error fetching trades by date range: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance", response_model=PerformanceStatsResponse)
async def get_performance_stats(strategy_id: Optional[str] = None):
    """
    Get performance statistics

    Args:
        strategy_id: Optional strategy filter

    Returns:
        Performance metrics including win rate, P&L, etc.
    """
    try:
        stats = trade_history.get_performance_stats(strategy_id)
        return stats
    except Exception as e:
        logger.error(f"Error calculating performance stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/csv")
async def export_trades_to_csv(filename: str = "trades_export.csv"):
    """
    Export trade history to CSV file

    Args:
        filename: Name of the CSV file

    Returns:
        Success message with file path
    """
    try:
        filepath = trade_history.export_to_csv(filename)
        if filepath:
            return {
                "success": True,
                "filepath": filepath,
                "message": f"Trades exported to {filepath}"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to export trades")
    except Exception as e:
        logger.error(f"Error exporting trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_trade_summary():
    """
    Get summary of recent trading activity

    Returns:
        Summary statistics for dashboard display
    """
    try:
        all_trades = trade_history.get_all_trades()
        recent_trades = trade_history.get_recent_trades(10)

        # Get performance stats
        stats = trade_history.get_performance_stats()

        # Get today's trades
        from datetime import datetime
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        today_trades = trade_history.get_trades_by_date_range(today_start, datetime.now().isoformat())

        # Calculate today's P&L
        today_pnl = sum(t.pnl for t in today_trades if t.pnl is not None)

        return {
            "total_trades": len(all_trades),
            "recent_trades": len(recent_trades),
            "today_trades": len(today_trades),
            "today_pnl": today_pnl,
            "win_rate": stats['win_rate'],
            "total_pnl": stats['total_pnl'],
            "profit_factor": stats['profit_factor']
        }
    except Exception as e:
        logger.error(f"Error generating trade summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/clear")
async def clear_trade_history():
    """
    Clear all trade history (use with caution!)

    Returns:
        Success message
    """
    try:
        trade_history.clear_history()
        return {
            "success": True,
            "message": "Trade history cleared"
        }
    except Exception as e:
        logger.error(f"Error clearing trade history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

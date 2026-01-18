"""Strategy management API endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class Strategy(BaseModel):
    """Strategy configuration"""
    id: str
    name: str
    description: str
    status: str  # 'active', 'paused', 'stopped'
    symbols: List[str]
    parameters: Dict[str, Any]


class StrategyPerformance(BaseModel):
    """Strategy performance metrics"""
    strategy_id: str
    total_pnl: float
    total_trades: int
    win_rate: float
    sharpe_ratio: float


@router.get("/list", response_model=List[Strategy])
async def list_strategies():
    """
    Get all available trading strategies.

    Returns list of strategies with their configurations.
    """
    # Mock strategies - integrate with strategy manager
    strategies = [
        {
            "id": "ma_crossover",
            "name": "Moving Average Crossover",
            "description": "Buy when fast MA crosses above slow MA",
            "status": "stopped",
            "symbols": ["AAPL", "MSFT"],
            "parameters": {
                "fast_period": 10,
                "slow_period": 30
            }
        },
        {
            "id": "rsi_mean_reversion",
            "name": "RSI Mean Reversion",
            "description": "Buy oversold, sell overbought based on RSI",
            "status": "stopped",
            "symbols": ["SPY"],
            "parameters": {
                "rsi_period": 14,
                "oversold": 30,
                "overbought": 70
            }
        }
    ]

    return strategies


@router.post("/{strategy_id}/start")
async def start_strategy(strategy_id: str):
    """Start a strategy execution"""
    logger.info(f"Starting strategy: {strategy_id}")
    return {
        "success": True,
        "strategy_id": strategy_id,
        "status": "active",
        "message": f"Strategy {strategy_id} started"
    }


@router.post("/{strategy_id}/stop")
async def stop_strategy(strategy_id: str):
    """Stop a running strategy"""
    logger.info(f"Stopping strategy: {strategy_id}")
    return {
        "success": True,
        "strategy_id": strategy_id,
        "status": "stopped",
        "message": f"Strategy {strategy_id} stopped"
    }


@router.get("/{strategy_id}/performance", response_model=StrategyPerformance)
async def get_strategy_performance(strategy_id: str):
    """Get performance metrics for a specific strategy"""
    # Mock performance data
    return StrategyPerformance(
        strategy_id=strategy_id,
        total_pnl=2500.00,
        total_trades=15,
        win_rate=66.7,
        sharpe_ratio=1.45
    )

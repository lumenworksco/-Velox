"""Position tracking API endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime

from backend.position_manager import position_manager

router = APIRouter()


class PositionResponse(BaseModel):
    """Position information"""
    symbol: str
    strategy_id: str
    shares: float
    entry_price: float
    entry_time: datetime
    stop_loss: float | None
    take_profit: float | None
    unrealized_pnl: float
    unrealized_pnl_percent: float


@router.get("/list", response_model=List[PositionResponse])
async def list_positions():
    """
    Get all open positions across all strategies
    """
    try:
        all_positions = position_manager.get_all_positions()

        # For now, use entry price as current price (in production, fetch live prices)
        positions_data = []
        for position in all_positions:
            # TODO: Fetch current price from market data
            current_price = position.entry_price  # Placeholder

            positions_data.append({
                "symbol": position.symbol,
                "strategy_id": position.strategy_id,
                "shares": position.shares,
                "entry_price": position.entry_price,
                "entry_time": position.entry_time,
                "stop_loss": position.stop_loss,
                "take_profit": position.take_profit,
                "unrealized_pnl": position.unrealized_pnl(current_price),
                "unrealized_pnl_percent": position.unrealized_pnl_percent(current_price)
            })

        return positions_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch positions: {str(e)}")


@router.get("/strategy/{strategy_id}", response_model=List[PositionResponse])
async def get_strategy_positions(strategy_id: str):
    """
    Get positions for a specific strategy
    """
    try:
        strategy_positions = position_manager.get_strategy_positions(strategy_id)

        positions_data = []
        for symbol, position in strategy_positions.items():
            current_price = position.entry_price  # Placeholder

            positions_data.append({
                "symbol": position.symbol,
                "strategy_id": position.strategy_id,
                "shares": position.shares,
                "entry_price": position.entry_price,
                "entry_time": position.entry_time,
                "stop_loss": position.stop_loss,
                "take_profit": position.take_profit,
                "unrealized_pnl": position.unrealized_pnl(current_price),
                "unrealized_pnl_percent": position.unrealized_pnl_percent(current_price)
            })

        return positions_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch positions: {str(e)}")

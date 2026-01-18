"""Trading API endpoints - Order placement and management"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging

from core import TradingEngine, TradingMode, TradingConfig

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize trading engine (singleton pattern)
trading_engine = None


def get_trading_engine():
    """Get or create trading engine instance"""
    global trading_engine
    if trading_engine is None:
        config = TradingConfig(mode=TradingMode.PAPER)
        trading_engine = TradingEngine(config)
    return trading_engine


# Pydantic models for request/response
class OrderRequest(BaseModel):
    """Order placement request"""
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: int
    order_type: str = 'market'  # 'market', 'limit', 'stop'
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None


class OrderResponse(BaseModel):
    """Order response"""
    order_id: str
    status: str
    symbol: str
    side: str
    quantity: int
    filled_qty: int
    avg_price: Optional[float]
    created_at: datetime


class PositionResponse(BaseModel):
    """Position information"""
    symbol: str
    quantity: int
    avg_entry_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_percent: float


@router.post("/orders", response_model=OrderResponse)
async def place_order(order: OrderRequest):
    """
    Place a new trading order.

    **Paper Trading Mode**: Orders are simulated
    **Live Trading Mode**: Orders are sent to Alpaca
    """
    try:
        engine = get_trading_engine()

        # Validate order
        if order.side not in ['buy', 'sell']:
            raise HTTPException(status_code=400, detail="Invalid side. Must be 'buy' or 'sell'")

        if order.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive")

        # Place order through trading engine
        result = engine.place_order(
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            order_type=order.order_type,
            limit_price=order.limit_price,
            stop_price=order.stop_price
        )

        return OrderResponse(
            order_id=result.get('id', 'unknown'),
            status=result.get('status', 'pending'),
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            filled_qty=result.get('filled_qty', 0),
            avg_price=result.get('avg_price'),
            created_at=datetime.now()
        )

    except Exception as e:
        logger.error(f"Error placing order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(status: Optional[str] = None):
    """
    Get all orders, optionally filtered by status.

    **Status values**: pending, filled, canceled, rejected
    """
    try:
        engine = get_trading_engine()
        orders = engine.get_orders(status=status)

        return [
            OrderResponse(
                order_id=o.get('id'),
                status=o.get('status'),
                symbol=o.get('symbol'),
                side=o.get('side'),
                quantity=o.get('quantity'),
                filled_qty=o.get('filled_qty', 0),
                avg_price=o.get('avg_price'),
                created_at=o.get('created_at', datetime.now())
            )
            for o in orders
        ]

    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/orders/{order_id}")
async def cancel_order(order_id: str):
    """Cancel an open order"""
    try:
        engine = get_trading_engine()
        result = engine.cancel_order(order_id)

        return {
            "success": True,
            "order_id": order_id,
            "status": "canceled"
        }

    except Exception as e:
        logger.error(f"Error canceling order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions", response_model=List[PositionResponse])
async def get_positions():
    """Get all open positions"""
    try:
        engine = get_trading_engine()
        positions = engine.get_positions()

        return [
            PositionResponse(
                symbol=p.get('symbol'),
                quantity=p.get('quantity'),
                avg_entry_price=p.get('avg_entry_price'),
                current_price=p.get('current_price'),
                market_value=p.get('market_value'),
                unrealized_pnl=p.get('unrealized_pnl'),
                unrealized_pnl_percent=p.get('unrealized_pnl_percent')
            )
            for p in positions
        ]

    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/positions/{symbol}/close")
async def close_position(symbol: str):
    """Close an entire position for a symbol"""
    try:
        engine = get_trading_engine()
        result = engine.close_position(symbol)

        return {
            "success": True,
            "symbol": symbol,
            "message": f"Position closed for {symbol}"
        }

    except Exception as e:
        logger.error(f"Error closing position: {e}")
        raise HTTPException(status_code=500, detail=str(e))

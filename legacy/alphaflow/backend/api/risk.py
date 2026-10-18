"""Risk management API endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.daily_risk_manager import daily_risk_manager

router = APIRouter()


class RiskStats(BaseModel):
    """Daily risk statistics"""
    date: str
    starting_value: float | None
    current_value: float | None
    daily_pnl: float
    daily_pnl_percent: float
    max_loss_limit: float
    trading_halted: bool
    halt_reason: str | None


@router.get("/daily-stats", response_model=RiskStats)
async def get_daily_risk_stats():
    """Get current daily risk statistics"""
    stats = daily_risk_manager.get_daily_stats()
    return stats


@router.post("/halt")
async def manual_halt():
    """Manually halt all trading"""
    daily_risk_manager.manual_halt("Manual halt by user")
    return {
        "success": True,
        "message": "Trading halted manually"
    }


@router.post("/resume")
async def resume_trading():
    """Resume trading (admin override)"""
    daily_risk_manager.resume_trading()
    return {
        "success": True,
        "message": "Trading resumed"
    }

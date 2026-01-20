"""System health and monitoring API endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
import os
import psutil
from datetime import datetime

from backend.position_manager import position_manager
from backend.daily_risk_manager import daily_risk_manager
from backend.trade_history import trade_history
from backend.portfolio_risk import portfolio_risk_manager
from backend.strategy_executor import strategy_executor

logger = logging.getLogger(__name__)
router = APIRouter()


class SystemHealthResponse(BaseModel):
    """System health response"""
    status: str  # 'healthy', 'degraded', 'critical'
    timestamp: str
    components: Dict[str, Any]
    alerts: List[str]
    recommendations: List[str]


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health():
    """
    Comprehensive system health check

    Returns:
        Detailed health status with component checks and recommendations
    """
    try:
        alerts = []
        recommendations = []
        status = "healthy"

        # 1. Check Alpaca API connection
        alpaca_configured = bool(os.getenv('ALPACA_API_KEY') and os.getenv('ALPACA_SECRET_KEY'))
        alpaca_connected = False
        account_value = 0.0

        if alpaca_configured and strategy_executor.trading_engine:
            try:
                account = strategy_executor.trading_engine.api.get_account()
                alpaca_connected = True
                account_value = float(account.portfolio_value)
            except Exception as e:
                alpaca_connected = False
                alerts.append(f"Alpaca API connection error: {str(e)}")
                status = "degraded"

        if not alpaca_configured:
            alerts.append("Alpaca API not configured")
            recommendations.append("Add ALPACA_API_KEY and ALPACA_SECRET_KEY to .env")
            status = "degraded"

        # 2. Check trading mode
        trading_mode = "paper" if os.getenv('ALPACA_PAPER', 'true').lower() == 'true' else "live"
        if trading_mode == "live":
            alerts.append("⚠️ LIVE TRADING MODE - Real money at risk")

        # 3. Check running strategies
        running_strategies = len([
            s for s in strategy_executor.running_strategies.values()
            if s['status'] == 'running'
        ])

        # 4. Check open positions
        all_positions = position_manager.get_all_positions()
        num_positions = len(all_positions)

        # 5. Check daily risk status
        daily_stats = daily_risk_manager.get_daily_stats()
        trading_halted = daily_stats.get('trading_halted', False)

        if trading_halted:
            alerts.append(f"⛔ Trading halted: {daily_stats.get('halt_reason')}")
            status = "critical"
            recommendations.append("Review daily loss limit and consider resuming trading")

        # 6. Check portfolio risk
        if num_positions > 0 and account_value > 0:
            # Convert positions to dict format for risk manager
            position_dicts = [
                {
                    'symbol': p.symbol,
                    'shares': p.shares,
                    'entry_price': p.entry_price,
                    'current_price': p.entry_price,  # Simplified
                    'stop_loss': p.stop_loss
                }
                for p in all_positions
            ]

            risk_report = portfolio_risk_manager.get_risk_report(position_dicts, account_value)

            if not risk_report['overall_risk_ok']:
                alerts.append("⚠️ Portfolio risk limits exceeded")
                status = "degraded"
                recommendations.append("Close some positions to reduce portfolio heat")

            # Add portfolio heat info
            heat = risk_report['portfolio_heat']
            if heat['current'] > heat['limit'] * 0.8:  # >80% of limit
                recommendations.append(f"Portfolio heat at {heat['current']*100:.1f}% (close to {heat['limit']*100:.0f}% limit)")

        # 7. Check system resources
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        if cpu_percent > 90:
            alerts.append(f"High CPU usage: {cpu_percent}%")
            status = "degraded"

        if memory.percent > 90:
            alerts.append(f"High memory usage: {memory.percent}%")
            status = "degraded"

        if disk.percent > 90:
            alerts.append(f"Low disk space: {disk.percent}% used")
            recommendations.append("Clean up disk space")

        # 8. Check trade history
        recent_trades = trade_history.get_recent_trades(10)
        total_trades = len(trade_history.get_all_trades())

        # 9. Check notification system
        from backend.notification_system import notification_system
        email_enabled = notification_system.email_enabled
        slack_enabled = notification_system.slack_enabled

        if not email_enabled and not slack_enabled:
            recommendations.append("Enable email or Slack notifications for trade alerts")

        # 10. Recommendations based on state
        if running_strategies == 0 and num_positions == 0:
            recommendations.append("No strategies running - start a strategy to begin trading")

        if num_positions > 10:
            recommendations.append(f"High number of positions ({num_positions}) - consider consolidating")

        if trading_mode == "paper" and total_trades > 50:
            recommendations.append("Consider switching to live trading after successful paper testing")

        # Build response
        return SystemHealthResponse(
            status=status,
            timestamp=datetime.now().isoformat(),
            components={
                "alpaca_api": {
                    "configured": alpaca_configured,
                    "connected": alpaca_connected,
                    "account_value": account_value if alpaca_connected else None
                },
                "trading": {
                    "mode": trading_mode,
                    "running_strategies": running_strategies,
                    "open_positions": num_positions,
                    "trading_halted": trading_halted
                },
                "risk": {
                    "daily_pnl": daily_stats.get('daily_pnl', 0.0),
                    "daily_pnl_percent": daily_stats.get('daily_pnl_percent', 0.0),
                    "max_loss_limit": daily_stats.get('max_loss_limit', 0.0)
                },
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "memory_available_gb": round(memory.available / (1024**3), 2)
                },
                "notifications": {
                    "email_enabled": email_enabled,
                    "slack_enabled": slack_enabled
                },
                "history": {
                    "total_trades": total_trades,
                    "recent_trades": len(recent_trades)
                }
            },
            alerts=alerts,
            recommendations=recommendations
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return SystemHealthResponse(
            status="critical",
            timestamp=datetime.now().isoformat(),
            components={},
            alerts=[f"Health check error: {str(e)}"],
            recommendations=["Check system logs for details"]
        )


@router.get("/status/quick")
async def get_quick_status():
    """
    Quick status check (for frequent polling)

    Returns:
        Essential status information
    """
    try:
        running_strategies = len([
            s for s in strategy_executor.running_strategies.values()
            if s['status'] == 'running'
        ])

        num_positions = len(position_manager.get_all_positions())
        daily_stats = daily_risk_manager.get_daily_stats()
        trading_mode = "paper" if os.getenv('ALPACA_PAPER', 'true').lower() == 'true' else "live"

        return {
            "status": "degraded" if daily_stats.get('trading_halted') else "healthy",
            "trading_mode": trading_mode,
            "running_strategies": running_strategies,
            "open_positions": num_positions,
            "trading_halted": daily_stats.get('trading_halted', False),
            "daily_pnl": daily_stats.get('daily_pnl', 0.0)
        }

    except Exception as e:
        logger.error(f"Quick status check failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/diagnostics")
async def get_diagnostics():
    """
    Detailed diagnostic information for troubleshooting

    Returns:
        Comprehensive diagnostic data
    """
    try:
        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "environment": {
                "alpaca_api_key_set": bool(os.getenv('ALPACA_API_KEY')),
                "alpaca_secret_set": bool(os.getenv('ALPACA_SECRET_KEY')),
                "alpaca_paper": os.getenv('ALPACA_PAPER', 'true'),
                "smtp_configured": bool(os.getenv('SMTP_USERNAME')),
                "slack_configured": bool(os.getenv('SLACK_WEBHOOK_URL'))
            },
            "strategies": {
                "total_strategies": len(strategy_executor.running_strategies),
                "running": [
                    {
                        "id": sid,
                        "status": info['status'],
                        "start_time": info['start_time'].isoformat(),
                        "symbols": info['config'].get('symbols', [])
                    }
                    for sid, info in strategy_executor.running_strategies.items()
                ]
            },
            "positions": {
                "total": len(position_manager.get_all_positions()),
                "by_strategy": {}
            },
            "performance": trade_history.get_performance_stats(),
            "system_resources": {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "process_memory_mb": psutil.Process().memory_info().rss / 1024 / 1024
            }
        }

        # Group positions by strategy
        for position in position_manager.get_all_positions():
            strategy_id = position.strategy_id
            if strategy_id not in diagnostics["positions"]["by_strategy"]:
                diagnostics["positions"]["by_strategy"][strategy_id] = []

            diagnostics["positions"]["by_strategy"][strategy_id].append({
                "symbol": position.symbol,
                "shares": position.shares,
                "entry_price": position.entry_price,
                "stop_loss": position.stop_loss
            })

        return diagnostics

    except Exception as e:
        logger.error(f"Diagnostics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

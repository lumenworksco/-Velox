"""Daily risk management and loss limits"""

import logging
from datetime import datetime, date
from typing import Optional

logger = logging.getLogger(__name__)


class DailyRiskManager:
    """Manages daily loss limits and risk controls"""

    def __init__(self, max_daily_loss_percent: float = 0.02):
        """
        Initialize daily risk manager

        Args:
            max_daily_loss_percent: Maximum daily loss as % of portfolio (default 2%)
        """
        self.max_daily_loss_percent = max_daily_loss_percent
        self.today = date.today()
        self.starting_portfolio_value: Optional[float] = None
        self.current_portfolio_value: Optional[float] = None
        self.daily_pnl: float = 0.0
        self.trading_halted: bool = False
        self.halt_reason: Optional[str] = None

    def reset_daily(self):
        """Reset daily tracking (called at start of new trading day)"""
        today = date.today()

        if today != self.today:
            logger.info(f"New trading day: {today}")
            self.today = today
            self.starting_portfolio_value = None
            self.current_portfolio_value = None
            self.daily_pnl = 0.0
            self.trading_halted = False
            self.halt_reason = None

    def update_portfolio_value(self, current_value: float):
        """
        Update current portfolio value and check limits

        Args:
            current_value: Current portfolio value

        Returns:
            True if trading should continue, False if halted
        """
        self.reset_daily()  # Auto-reset if new day

        # Set starting value on first update of the day
        if self.starting_portfolio_value is None:
            self.starting_portfolio_value = current_value
            logger.info(f"Daily starting portfolio value: ${current_value:,.2f}")

        self.current_portfolio_value = current_value

        # Calculate daily P&L
        if self.starting_portfolio_value:
            self.daily_pnl = current_value - self.starting_portfolio_value
            daily_pnl_percent = (self.daily_pnl / self.starting_portfolio_value) * 100

            # Check daily loss limit
            if daily_pnl_percent <= -(self.max_daily_loss_percent * 100):
                if not self.trading_halted:
                    self.trading_halted = True
                    self.halt_reason = f"Daily loss limit reached: {daily_pnl_percent:.2f}% (limit: -{self.max_daily_loss_percent * 100}%)"
                    logger.error(f"🚨 TRADING HALTED: {self.halt_reason}")
                return False

        return True

    def can_trade(self) -> tuple[bool, Optional[str]]:
        """
        Check if trading is allowed

        Returns:
            (can_trade, reason_if_not)
        """
        self.reset_daily()

        if self.trading_halted:
            return False, self.halt_reason

        return True, None

    def get_daily_stats(self) -> dict:
        """Get current daily statistics"""
        self.reset_daily()

        if self.starting_portfolio_value is None:
            return {
                "date": self.today.isoformat(),
                "starting_value": None,
                "current_value": None,
                "daily_pnl": 0.0,
                "daily_pnl_percent": 0.0,
                "max_loss_limit": self.max_daily_loss_percent * 100,
                "trading_halted": False,
                "halt_reason": None
            }

        daily_pnl_percent = 0.0
        if self.starting_portfolio_value:
            daily_pnl_percent = (self.daily_pnl / self.starting_portfolio_value) * 100

        return {
            "date": self.today.isoformat(),
            "starting_value": self.starting_portfolio_value,
            "current_value": self.current_portfolio_value,
            "daily_pnl": self.daily_pnl,
            "daily_pnl_percent": daily_pnl_percent,
            "max_loss_limit": self.max_daily_loss_percent * 100,
            "trading_halted": self.trading_halted,
            "halt_reason": self.halt_reason
        }

    def manual_halt(self, reason: str = "Manual halt"):
        """Manually halt trading"""
        self.trading_halted = True
        self.halt_reason = reason
        logger.warning(f"Trading manually halted: {reason}")

    def resume_trading(self):
        """Resume trading (admin override)"""
        self.trading_halted = False
        self.halt_reason = None
        logger.info("Trading resumed by admin")


# Global risk manager instance
daily_risk_manager = DailyRiskManager(max_daily_loss_percent=0.02)  # 2% max daily loss

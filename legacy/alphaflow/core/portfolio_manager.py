"""Portfolio Manager - Stub implementation for backward compatibility."""

import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class PortfolioManager:
    """Manages portfolio positions and P&L tracking.

    Note: This is a stub implementation for backward compatibility.
    Production portfolio management is handled by backend/position_manager.py
    """

    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, dict] = {}
        logger.info(f"PortfolioManager initialized with ${initial_capital:,.2f}")

    def sync_with_alpaca_account(self, cash_balance: float):
        """Sync cash balance with Alpaca account"""
        self.cash = cash_balance
        logger.info(f"Synced cash balance: ${cash_balance:,.2f}")

    def add_position(self, symbol: str, quantity: int, entry_price: float,
                     stop_loss: float = None, take_profit: float = None):
        """Add a new position"""
        self.positions[symbol] = {
            'symbol': symbol,
            'quantity': quantity,
            'entry_price': entry_price,
            'current_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'entry_time': datetime.now()
        }
        cost = quantity * entry_price
        self.cash -= cost
        logger.info(f"Added position: {quantity} shares of {symbol} @ ${entry_price:.2f}")

    def close_position(self, symbol: str, exit_price: float):
        """Close an existing position"""
        if symbol in self.positions:
            position = self.positions[symbol]
            proceeds = position['quantity'] * exit_price
            self.cash += proceeds
            del self.positions[symbol]
            logger.info(f"Closed position: {symbol} @ ${exit_price:.2f}")
        else:
            logger.warning(f"Cannot close position - {symbol} not found")

    def update_prices(self, prices: Dict[str, float]):
        """Update current prices for all positions"""
        for symbol, price in prices.items():
            if symbol in self.positions:
                self.positions[symbol]['current_price'] = price

    def get_summary(self) -> dict:
        """Get portfolio summary"""
        total_value = self.cash
        for position in self.positions.values():
            total_value += position['quantity'] * position['current_price']

        return {
            'cash': self.cash,
            'total_value': total_value,
            'positions': list(self.positions.values()),
            'pnl': total_value - self.initial_capital,
            'pnl_percent': ((total_value - self.initial_capital) / self.initial_capital) * 100
        }

"""Position tracking and management for active trades"""

import logging
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Represents an open position"""
    symbol: str
    strategy_id: str
    shares: float
    entry_price: float
    entry_time: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    @property
    def entry_value(self) -> float:
        """Total value at entry"""
        return self.shares * self.entry_price

    def unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized P&L"""
        return (current_price - self.entry_price) * self.shares

    def unrealized_pnl_percent(self, current_price: float) -> float:
        """Calculate unrealized P&L percentage"""
        return ((current_price - self.entry_price) / self.entry_price) * 100


class PositionManager:
    """Manages open positions for all strategies"""

    def __init__(self):
        # {strategy_id: {symbol: Position}}
        self.positions: Dict[str, Dict[str, Position]] = {}

    def has_position(self, strategy_id: str, symbol: str) -> bool:
        """Check if strategy has an open position in symbol"""
        return (strategy_id in self.positions and
                symbol in self.positions[strategy_id])

    def add_position(
        self,
        strategy_id: str,
        symbol: str,
        shares: float,
        entry_price: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Position:
        """Add a new position"""
        position = Position(
            symbol=symbol,
            strategy_id=strategy_id,
            shares=shares,
            entry_price=entry_price,
            entry_time=datetime.now(),
            stop_loss=stop_loss,
            take_profit=take_profit
        )

        if strategy_id not in self.positions:
            self.positions[strategy_id] = {}

        self.positions[strategy_id][symbol] = position
        logger.info(f"Added position: {strategy_id} - {shares} {symbol} @ ${entry_price:.2f}")

        return position

    def remove_position(self, strategy_id: str, symbol: str) -> Optional[Position]:
        """Remove and return a position"""
        if not self.has_position(strategy_id, symbol):
            logger.warning(f"Cannot remove position - not found: {strategy_id}/{symbol}")
            return None

        position = self.positions[strategy_id].pop(symbol)
        logger.info(f"Removed position: {strategy_id} - {position.shares} {symbol}")

        # Clean up empty strategy dict
        if not self.positions[strategy_id]:
            del self.positions[strategy_id]

        return position

    def get_position(self, strategy_id: str, symbol: str) -> Optional[Position]:
        """Get a specific position"""
        if not self.has_position(strategy_id, symbol):
            return None
        return self.positions[strategy_id][symbol]

    def get_strategy_positions(self, strategy_id: str) -> Dict[str, Position]:
        """Get all positions for a strategy"""
        return self.positions.get(strategy_id, {})

    def get_all_positions(self) -> List[Position]:
        """Get all positions across all strategies"""
        all_positions = []
        for strategy_positions in self.positions.values():
            all_positions.extend(strategy_positions.values())
        return all_positions

    def get_position_count(self, strategy_id: Optional[str] = None) -> int:
        """Get total number of open positions"""
        if strategy_id:
            return len(self.positions.get(strategy_id, {}))
        else:
            return sum(len(positions) for positions in self.positions.values())

    def check_stop_loss(self, current_price: float, position: Position) -> bool:
        """Check if stop loss should be triggered"""
        if position.stop_loss is None:
            return False

        # For long positions, stop loss is below entry
        return current_price <= position.stop_loss

    def check_take_profit(self, current_price: float, position: Position) -> bool:
        """Check if take profit should be triggered"""
        if position.take_profit is None:
            return False

        # For long positions, take profit is above entry
        return current_price >= position.take_profit

    def clear_strategy_positions(self, strategy_id: str) -> int:
        """Remove all positions for a strategy"""
        if strategy_id not in self.positions:
            return 0

        count = len(self.positions[strategy_id])
        del self.positions[strategy_id]
        logger.info(f"Cleared {count} positions for strategy {strategy_id}")
        return count

    def get_total_exposure(self, current_prices: Dict[str, float]) -> float:
        """Calculate total market exposure across all positions"""
        total = 0.0
        for strategy_positions in self.positions.values():
            for symbol, position in strategy_positions.items():
                current_price = current_prices.get(symbol, position.entry_price)
                total += position.shares * current_price
        return total

    def get_total_unrealized_pnl(self, current_prices: Dict[str, float]) -> float:
        """Calculate total unrealized P&L across all positions"""
        total_pnl = 0.0
        for strategy_positions in self.positions.values():
            for symbol, position in strategy_positions.items():
                current_price = current_prices.get(symbol, position.entry_price)
                total_pnl += position.unrealized_pnl(current_price)
        return total_pnl


# Global position manager instance
position_manager = PositionManager()

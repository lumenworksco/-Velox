"""Portfolio Manager for Version 6 Trading App."""

import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

from .config import TradingConfig
from .data_structures import Position, TradeRecord, PortfolioSnapshot


class PortfolioManager:
    """Manages portfolio positions and tracks performance."""
    
    def __init__(self, initial_capital: float = TradingConfig.DEFAULT_INITIAL_CAPITAL):
        self.logger = logging.getLogger(__name__)
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[TradeRecord] = []
        self.snapshots: List[PortfolioSnapshot] = []
        self.start_date = datetime.now()
    
    def add_position(self, symbol: str, quantity: int, price: float,
                    strategy: str, stop_loss: float = None,
                    take_profit: float = None) -> bool:
        """Add a new position or add to existing position."""
        
        cost = quantity * price
        
        if cost > self.cash:
            self.logger.warning(f"Insufficient cash for {symbol} position")
            return False
        
        if symbol in self.positions:
            # Add to existing position
            existing = self.positions[symbol]
            total_quantity = existing.quantity + quantity
            avg_price = ((existing.quantity * existing.entry_price) + cost) / total_quantity
            
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=total_quantity,
                entry_price=avg_price,
                current_price=price,
                entry_time=existing.entry_time,
                strategy=strategy,
                stop_loss=stop_loss or existing.stop_loss,
                take_profit=take_profit or existing.take_profit
            )
        else:
            # New position
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                entry_price=price,
                current_price=price,
                entry_time=datetime.now(),
                strategy=strategy,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
        
        self.cash -= cost
        
        # Record trade
        self.trade_history.append(TradeRecord(
            symbol=symbol,
            action="BUY",
            entry_price=price,
            quantity=quantity,
            entry_time=datetime.now(),
            strategy=strategy
        ))
        
        self.logger.info(f"Added position: {quantity} {symbol} @ ${price:.2f}")
        return True
    
    def close_position(self, symbol: str, price: float,
                      quantity: int = None) -> Optional[TradeRecord]:
        """Close a position or reduce it."""
        
        if symbol not in self.positions:
            self.logger.warning(f"No position in {symbol} to close")
            return None
        
        position = self.positions[symbol]
        close_quantity = quantity or position.quantity
        close_quantity = min(close_quantity, position.quantity)
        
        # Calculate P&L
        proceeds = close_quantity * price
        cost_basis = close_quantity * position.entry_price
        pnl = proceeds - cost_basis
        pnl_percent = (pnl / cost_basis) * 100 if cost_basis > 0 else 0
        
        self.cash += proceeds
        
        # Update or remove position
        if close_quantity >= position.quantity:
            del self.positions[symbol]
        else:
            self.positions[symbol].quantity -= close_quantity
        
        # Create trade record
        trade = TradeRecord(
            symbol=symbol,
            action="SELL",
            entry_price=position.entry_price,
            quantity=close_quantity,
            entry_time=position.entry_time,
            strategy=position.strategy,
            exit_price=price,
            exit_time=datetime.now(),
            pnl=pnl,
            pnl_percent=pnl_percent,
            status="CLOSED"
        )
        
        self.trade_history.append(trade)
        
        self.logger.info(
            f"Closed position: {close_quantity} {symbol} @ ${price:.2f} "
            f"(P&L: ${pnl:.2f}, {pnl_percent:.2f}%)"
        )
        
        return trade
    
    def update_prices(self, prices: Dict[str, float]):
        """Update current prices for all positions."""
        
        for symbol, price in prices.items():
            if symbol in self.positions:
                self.positions[symbol].current_price = price
    
    def get_portfolio_value(self) -> float:
        """Get total portfolio value (cash + positions)."""
        
        positions_value = sum(p.market_value for p in self.positions.values())
        return self.cash + positions_value
    
    def get_positions_value(self) -> float:
        """Get total value of all positions."""
        return sum(p.market_value for p in self.positions.values())
    
    def get_unrealized_pnl(self) -> float:
        """Get total unrealized P&L."""
        return sum(p.unrealized_pnl for p in self.positions.values())
    
    def get_realized_pnl(self) -> float:
        """Get total realized P&L from closed trades."""
        return sum(t.pnl for t in self.trade_history if t.status == "CLOSED")
    
    def get_total_pnl(self) -> float:
        """Get total P&L (realized + unrealized)."""
        return self.get_realized_pnl() + self.get_unrealized_pnl()
    
    def get_summary(self) -> Dict:
        """Get portfolio summary."""
        
        portfolio_value = self.get_portfolio_value()
        total_pnl = portfolio_value - self.initial_capital
        total_pnl_percent = (total_pnl / self.initial_capital) * 100
        
        # Calculate win rate
        closed_trades = [t for t in self.trade_history if t.status == "CLOSED"]
        winning_trades = [t for t in closed_trades if t.pnl > 0]
        win_rate = len(winning_trades) / len(closed_trades) if closed_trades else 0
        
        return {
            'initial_capital': self.initial_capital,
            'cash': self.cash,
            'positions_value': self.get_positions_value(),
            'portfolio_value': portfolio_value,
            'unrealized_pnl': self.get_unrealized_pnl(),
            'realized_pnl': self.get_realized_pnl(),
            'total_pnl': total_pnl,
            'total_pnl_percent': total_pnl_percent,
            'positions_count': len(self.positions),
            'total_trades': len(self.trade_history),
            'closed_trades': len(closed_trades),
            'win_rate': win_rate,
            'start_date': self.start_date
        }
    
    def get_positions_df(self) -> pd.DataFrame:
        """Get positions as a DataFrame."""
        
        if not self.positions:
            return pd.DataFrame()
        
        data = [p.to_dict() for p in self.positions.values()]
        return pd.DataFrame(data)
    
    def get_trades_df(self) -> pd.DataFrame:
        """Get trade history as a DataFrame."""
        
        if not self.trade_history:
            return pd.DataFrame()
        
        data = [t.to_dict() for t in self.trade_history]
        return pd.DataFrame(data)
    
    def take_snapshot(self) -> PortfolioSnapshot:
        """Take a snapshot of current portfolio state."""
        
        portfolio_value = self.get_portfolio_value()
        total_pnl = portfolio_value - self.initial_capital
        
        # Calculate daily P&L (simplified - compares to last snapshot)
        daily_pnl = 0.0
        if self.snapshots:
            daily_pnl = portfolio_value - self.snapshots[-1].total_value
        
        snapshot = PortfolioSnapshot(
            timestamp=datetime.now(),
            cash=self.cash,
            positions_value=self.get_positions_value(),
            total_value=portfolio_value,
            daily_pnl=daily_pnl,
            daily_pnl_percent=(daily_pnl / portfolio_value) * 100 if portfolio_value > 0 else 0,
            total_pnl=total_pnl,
            total_pnl_percent=(total_pnl / self.initial_capital) * 100,
            positions_count=len(self.positions)
        )
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def sync_with_alpaca_account(self, cash: float):
        """Sync portfolio with Alpaca account cash."""
        self.cash = cash
        self.initial_capital = max(self.initial_capital, cash)

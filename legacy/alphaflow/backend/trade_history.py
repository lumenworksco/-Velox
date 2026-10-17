"""Trade history tracking and database logging"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class TradeType(Enum):
    """Trade type enumeration"""
    BUY = "buy"
    SELL = "sell"


class TradeStatus(Enum):
    """Trade status enumeration"""
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Trade:
    """Represents a completed trade"""
    trade_id: str
    timestamp: str
    strategy_id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    shares: float
    price: float
    order_type: str  # 'market', 'limit', etc.
    status: str
    commission: float = 0.0
    pnl: Optional[float] = None  # Only for sell trades
    pnl_percent: Optional[float] = None  # Only for sell trades
    entry_price: Optional[float] = None  # Only for sell trades
    hold_duration: Optional[str] = None  # Only for sell trades (e.g., "2h 15m")
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    notes: Optional[str] = None
    alpaca_order_id: Optional[str] = None


class TradeHistory:
    """Manages trade history with JSON file persistence"""

    def __init__(self, history_file: str = "trade_history.json"):
        """
        Initialize trade history manager

        Args:
            history_file: Path to JSON file for storing trades
        """
        self.history_file = Path.cwd() / "logs" / history_file
        self.history_file.parent.mkdir(exist_ok=True)
        self._trades: List[Trade] = []
        self._load_history()

    def _load_history(self):
        """Load trade history from JSON file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self._trades = [Trade(**trade) for trade in data]
                logger.info(f"Loaded {len(self._trades)} trades from history")
            except Exception as e:
                logger.error(f"Failed to load trade history: {e}")
                self._trades = []
        else:
            logger.info("No existing trade history found, starting fresh")
            self._trades = []

    def _save_history(self):
        """Save trade history to JSON file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump([asdict(trade) for trade in self._trades], f, indent=2)
            logger.debug(f"Saved {len(self._trades)} trades to history")
        except Exception as e:
            logger.error(f"Failed to save trade history: {e}")

    def log_trade(
        self,
        strategy_id: str,
        symbol: str,
        side: str,
        shares: float,
        price: float,
        order_type: str = "market",
        status: str = "filled",
        commission: float = 0.0,
        pnl: Optional[float] = None,
        pnl_percent: Optional[float] = None,
        entry_price: Optional[float] = None,
        hold_duration: Optional[str] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        notes: Optional[str] = None,
        alpaca_order_id: Optional[str] = None
    ) -> Trade:
        """
        Log a new trade to history

        Args:
            strategy_id: Strategy that executed the trade
            symbol: Stock symbol
            side: 'buy' or 'sell'
            shares: Number of shares
            price: Execution price
            order_type: Order type (market, limit, etc.)
            status: Trade status (filled, cancelled, etc.)
            commission: Commission paid
            pnl: Profit/loss (for sell trades)
            pnl_percent: P&L percentage (for sell trades)
            entry_price: Entry price (for sell trades)
            hold_duration: How long position was held (for sell trades)
            stop_loss: Stop-loss level
            take_profit: Take-profit level
            notes: Additional notes (e.g., "stop_loss_triggered")
            alpaca_order_id: Alpaca order ID

        Returns:
            Trade object
        """
        trade = Trade(
            trade_id=f"{strategy_id}_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            strategy_id=strategy_id,
            symbol=symbol,
            side=side,
            shares=shares,
            price=price,
            order_type=order_type,
            status=status,
            commission=commission,
            pnl=pnl,
            pnl_percent=pnl_percent,
            entry_price=entry_price,
            hold_duration=hold_duration,
            stop_loss=stop_loss,
            take_profit=take_profit,
            notes=notes,
            alpaca_order_id=alpaca_order_id
        )

        self._trades.append(trade)
        self._save_history()

        # Log to console
        if side == 'buy':
            logger.info(f"📝 TRADE LOGGED: BUY {shares} {symbol} @ ${price:.2f} via {strategy_id}")
        else:
            pnl_str = f" | P&L: {'+' if pnl >= 0 else ''}{pnl:.2f} ({'+' if pnl_percent >= 0 else ''}{pnl_percent:.2f}%)" if pnl is not None else ""
            logger.info(f"📝 TRADE LOGGED: SELL {shares} {symbol} @ ${price:.2f} via {strategy_id}{pnl_str}")

        return trade

    def get_all_trades(self) -> List[Trade]:
        """Get all trades"""
        return self._trades.copy()

    def get_trades_by_strategy(self, strategy_id: str) -> List[Trade]:
        """Get trades for a specific strategy"""
        return [t for t in self._trades if t.strategy_id == strategy_id]

    def get_trades_by_symbol(self, symbol: str) -> List[Trade]:
        """Get trades for a specific symbol"""
        return [t for t in self._trades if t.symbol == symbol]

    def get_recent_trades(self, limit: int = 50) -> List[Trade]:
        """Get most recent trades"""
        return self._trades[-limit:]

    def get_trades_by_date_range(self, start_date: str, end_date: str) -> List[Trade]:
        """Get trades within a date range"""
        return [
            t for t in self._trades
            if start_date <= t.timestamp <= end_date
        ]

    def get_performance_stats(self, strategy_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate performance statistics

        Args:
            strategy_id: Optional strategy filter

        Returns:
            Dictionary with performance metrics
        """
        trades = self.get_trades_by_strategy(strategy_id) if strategy_id else self._trades

        # Filter for completed sell trades with P&L
        sell_trades = [t for t in trades if t.side == 'sell' and t.pnl is not None]

        if not sell_trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "avg_pnl": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "largest_win": 0.0,
                "largest_loss": 0.0,
                "profit_factor": 0.0
            }

        winning_trades = [t for t in sell_trades if t.pnl > 0]
        losing_trades = [t for t in sell_trades if t.pnl < 0]

        total_pnl = sum(t.pnl for t in sell_trades)
        total_wins = sum(t.pnl for t in winning_trades)
        total_losses = abs(sum(t.pnl for t in losing_trades))

        return {
            "total_trades": len(sell_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": (len(winning_trades) / len(sell_trades) * 100) if sell_trades else 0.0,
            "total_pnl": total_pnl,
            "avg_pnl": total_pnl / len(sell_trades) if sell_trades else 0.0,
            "avg_win": total_wins / len(winning_trades) if winning_trades else 0.0,
            "avg_loss": total_losses / len(losing_trades) if losing_trades else 0.0,
            "largest_win": max((t.pnl for t in winning_trades), default=0.0),
            "largest_loss": min((t.pnl for t in losing_trades), default=0.0),
            "profit_factor": (total_wins / total_losses) if total_losses > 0 else 0.0
        }

    def export_to_csv(self, filename: str = "trades_export.csv"):
        """Export trade history to CSV"""
        import csv

        export_path = Path.cwd() / "logs" / filename

        try:
            with open(export_path, 'w', newline='') as f:
                if not self._trades:
                    logger.warning("No trades to export")
                    return

                fieldnames = list(asdict(self._trades[0]).keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for trade in self._trades:
                    writer.writerow(asdict(trade))

            logger.info(f"Exported {len(self._trades)} trades to {export_path}")
            return str(export_path)
        except Exception as e:
            logger.error(f"Failed to export trades: {e}")
            return None

    def clear_history(self):
        """Clear all trade history (use with caution!)"""
        self._trades = []
        self._save_history()
        logger.warning("Trade history cleared")


# Global trade history instance
trade_history = TradeHistory()

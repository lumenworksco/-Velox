"""Risk Manager for Version 6 Trading App."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .config import TradingConfig
from .data_structures import TradeSignal, Position


class RiskManager:
    """Manages trading risk and position sizing."""
    
    def __init__(self, initial_capital: float = TradingConfig.DEFAULT_INITIAL_CAPITAL):
        self.logger = logging.getLogger(__name__)
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.max_drawdown_reached = 0.0
        self.peak_value = initial_capital
        self.trade_history = []
        self.last_reset_date = datetime.now().date()
    
    def reset_daily_stats(self):
        """Reset daily statistics."""
        today = datetime.now().date()
        if today != self.last_reset_date:
            self.daily_pnl = 0.0
            self.daily_trades = 0
            self.last_reset_date = today
    
    def update_capital(self, new_capital: float):
        """Update current capital and track drawdown."""
        self.current_capital = new_capital
        
        # Update peak
        if new_capital > self.peak_value:
            self.peak_value = new_capital
        
        # Calculate drawdown
        if self.peak_value > 0:
            drawdown = (self.peak_value - new_capital) / self.peak_value
            if drawdown > self.max_drawdown_reached:
                self.max_drawdown_reached = drawdown
    
    def calculate_position_size(self, signal: TradeSignal, 
                               current_price: float) -> int:
        """Calculate optimal position size based on risk parameters."""
        
        # Maximum position value based on portfolio percentage
        max_position_value = self.current_capital * TradingConfig.MAX_POSITION_SIZE
        
        # Calculate risk per share
        if signal.stop_loss:
            risk_per_share = abs(current_price - signal.stop_loss)
        else:
            risk_per_share = current_price * 0.02  # Default 2% risk
        
        # Risk-based position sizing (risk 1% of capital per trade)
        risk_amount = self.current_capital * 0.01
        risk_based_shares = int(risk_amount / risk_per_share) if risk_per_share > 0 else 0
        
        # Calculate shares based on max position size
        max_shares = int(max_position_value / current_price) if current_price > 0 else 0
        
        # Adjust by confidence
        confidence_multiplier = min(1.0, signal.confidence)
        adjusted_shares = int(min(risk_based_shares, max_shares) * confidence_multiplier)
        
        # Minimum 1 share if any signal
        return max(1, adjusted_shares) if adjusted_shares > 0 else 0
    
    def check_risk_limits(self, signal: TradeSignal, 
                         current_positions: List[Position]) -> Dict:
        """Check if trade passes risk limits."""
        
        self.reset_daily_stats()
        
        result = {
            'approved': True,
            'reasons': [],
            'warnings': []
        }
        
        # Check daily loss limit
        if self.daily_pnl < -self.initial_capital * TradingConfig.MAX_DAILY_LOSS:
            result['approved'] = False
            result['reasons'].append(
                f"Daily loss limit reached ({self.daily_pnl:.2f})"
            )
        
        # Check maximum drawdown
        current_drawdown = (self.peak_value - self.current_capital) / self.peak_value
        if current_drawdown > TradingConfig.MAX_DRAWDOWN:
            result['approved'] = False
            result['reasons'].append(
                f"Maximum drawdown reached ({current_drawdown:.1%})"
            )
        
        # Check existing positions in same symbol
        existing_position = next(
            (p for p in current_positions if p.symbol == signal.symbol), None
        )
        if existing_position:
            result['warnings'].append(
                f"Already have position in {signal.symbol}"
            )
        
        # Check total positions
        if len(current_positions) >= 10:
            result['warnings'].append("Maximum positions reached (10)")
            result['approved'] = False
            result['reasons'].append("Too many open positions")
        
        # Check minimum confidence
        if signal.confidence < TradingConfig.MIN_CONFIDENCE:
            result['approved'] = False
            result['reasons'].append(
                f"Confidence too low ({signal.confidence:.1%} < {TradingConfig.MIN_CONFIDENCE:.1%})"
            )
        
        return result
    
    def should_stop_trading(self, daily_loss: float, 
                           portfolio_value: float) -> bool:
        """Check if trading should stop due to risk limits."""
        
        # Daily loss limit
        if daily_loss < -self.initial_capital * TradingConfig.MAX_DAILY_LOSS:
            self.logger.warning("Daily loss limit breached")
            return True
        
        # Maximum drawdown
        drawdown = (self.initial_capital - portfolio_value) / self.initial_capital
        if drawdown > TradingConfig.MAX_DRAWDOWN:
            self.logger.warning(f"Maximum drawdown breached: {drawdown:.1%}")
            return True
        
        return False
    
    def get_risk_metrics(self) -> Dict:
        """Get current risk metrics."""
        
        current_drawdown = 0.0
        if self.peak_value > 0:
            current_drawdown = (self.peak_value - self.current_capital) / self.peak_value
        
        return {
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'peak_value': self.peak_value,
            'current_drawdown': current_drawdown,
            'max_drawdown_reached': self.max_drawdown_reached,
            'daily_pnl': self.daily_pnl,
            'daily_trades': self.daily_trades,
            'pnl_percent': ((self.current_capital / self.initial_capital) - 1) * 100
        }
    
    def record_trade(self, pnl: float):
        """Record a completed trade."""
        self.daily_pnl += pnl
        self.daily_trades += 1
        self.trade_history.append({
            'pnl': pnl,
            'timestamp': datetime.now()
        })
    
    def get_risk_summary(self) -> Dict:
        """Alias for get_risk_metrics for compatibility."""
        return self.get_risk_metrics()

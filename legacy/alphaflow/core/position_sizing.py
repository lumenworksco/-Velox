"""
Advanced Position Sizing Algorithms
Implements Kelly Criterion, volatility-adjusted sizing, and portfolio heat management
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class PositionSizeMethod(Enum):
    """Position sizing methods"""
    FIXED_DOLLAR = "fixed_dollar"
    FIXED_PERCENT = "fixed_percent"
    KELLY_CRITERION = "kelly_criterion"
    VOLATILITY_ADJUSTED = "volatility_adjusted"
    RISK_PARITY = "risk_parity"


@dataclass
class PositionSize:
    """Position size calculation result"""
    shares: int
    dollar_amount: float
    percent_of_portfolio: float
    risk_amount: float
    method: PositionSizeMethod
    reasoning: str


@dataclass
class Position:
    """Open position"""
    symbol: str
    shares: int
    entry_price: float
    current_price: float
    stop_loss: float
    take_profit: float


class KellyCriterionCalculator:
    """
    Optimal position sizing using Kelly Criterion

    Formula: f* = (bp - q) / b
    where:
        f* = fraction of capital to bet
        b = odds received (reward/risk ratio)
        p = probability of winning
        q = probability of losing (1-p)

    Safety measures:
    - Use fractional Kelly (0.25 to 0.5 of full Kelly)
    - Cap maximum position size at 25% of portfolio
    - Require minimum win rate of 40%
    """

    def __init__(self, fraction: float = 0.5, max_position: float = 0.25):
        """
        Args:
            fraction: Fraction of Kelly to use (0.5 = half Kelly, safer)
            max_position: Maximum position size as fraction of portfolio
        """
        self.logger = logging.getLogger(__name__)
        self.fraction = fraction  # Half Kelly for safety
        self.max_position = max_position

    def calculate_position_size(
        self,
        win_rate: float,
        reward_risk_ratio: float,
        portfolio_value: float
    ) -> float:
        """
        Calculate optimal position size using Kelly Criterion

        Args:
            win_rate: Historical win rate (0.0 to 1.0)
            reward_risk_ratio: Average win / Average loss
            portfolio_value: Total portfolio value

        Returns:
            Position size in dollars
        """
        try:
            # Validate inputs
            if win_rate < 0.4 or win_rate > 1.0:
                self.logger.warning(f"Invalid win rate: {win_rate}, using minimum size")
                return portfolio_value * 0.05  # 5% minimum

            if reward_risk_ratio <= 0:
                self.logger.warning(f"Invalid reward/risk ratio: {reward_risk_ratio}")
                return portfolio_value * 0.05

            # Kelly formula
            p = win_rate
            q = 1 - p
            b = reward_risk_ratio

            kelly_fraction = (b * p - q) / b

            # Apply safety fraction (half Kelly or quarter Kelly)
            safe_kelly = kelly_fraction * self.fraction

            # Ensure non-negative
            safe_kelly = max(0, safe_kelly)

            # Cap at maximum position size
            safe_kelly = min(safe_kelly, self.max_position)

            # Calculate dollar amount
            position_size = portfolio_value * safe_kelly

            self.logger.info(
                f"Kelly calculation: win_rate={win_rate:.2%}, R:R={reward_risk_ratio:.2f}, "
                f"kelly={kelly_fraction:.2%}, safe_kelly={safe_kelly:.2%}"
            )

            return position_size

        except Exception as e:
            self.logger.error(f"Error calculating Kelly position size: {e}")
            return portfolio_value * 0.05  # Default to 5%


class VolatilityAdjustedSizing:
    """
    Adjust position size based on volatility (ATR)

    Concept: Risk the same dollar amount on each trade
    - High volatility → wider stops → fewer shares
    - Low volatility → tighter stops → more shares

    Formula: Shares = Risk Amount / (Stop Distance)
    """

    def __init__(self, risk_per_trade_pct: float = 0.01):
        """
        Args:
            risk_per_trade_pct: Risk per trade as % of portfolio (default 1%)
        """
        self.logger = logging.getLogger(__name__)
        self.risk_per_trade_pct = risk_per_trade_pct

    def calculate_shares(
        self,
        price: float,
        atr: float,
        portfolio_value: float,
        stop_multiplier: float = 2.0
    ) -> int:
        """
        Calculate number of shares based on ATR

        Args:
            price: Current stock price
            atr: Average True Range
            portfolio_value: Total portfolio value
            stop_multiplier: ATR multiplier for stop distance (default 2x)

        Returns:
            Number of shares to buy
        """
        try:
            # Risk amount per trade (in dollars)
            risk_amount = portfolio_value * self.risk_per_trade_pct

            # Stop loss distance
            stop_distance = stop_multiplier * atr

            # Calculate shares
            shares = int(risk_amount / stop_distance)

            # Ensure at least 1 share
            shares = max(1, shares)

            # Ensure position size doesn't exceed 25% of portfolio
            max_shares = int((portfolio_value * 0.25) / price)
            shares = min(shares, max_shares)

            self.logger.info(
                f"Volatility-adjusted sizing: price=${price:.2f}, ATR=${atr:.2f}, "
                f"risk=${risk_amount:.2f}, stop_distance=${stop_distance:.2f}, shares={shares}"
            )

            return shares

        except Exception as e:
            self.logger.error(f"Error calculating volatility-adjusted size: {e}")
            return 1  # Minimum 1 share


class PortfolioHeatManager:
    """
    Manage total portfolio risk exposure

    Portfolio "heat" = sum of all position risks
    - Each position risk = |entry - stop| * shares
    - Maximum heat: 6% of portfolio
    - Warning heat: 4% of portfolio

    Actions:
    - Heat > 6%: Stop trading
    - Heat > 4%: Reduce new position sizes by 50%
    - Heat < 4%: Normal trading
    """

    def __init__(
        self,
        max_heat_pct: float = 0.06,
        warning_heat_pct: float = 0.04
    ):
        """
        Args:
            max_heat_pct: Maximum total portfolio risk (default 6%)
            warning_heat_pct: Warning threshold (default 4%)
        """
        self.logger = logging.getLogger(__name__)
        self.max_heat_pct = max_heat_pct
        self.warning_heat_pct = warning_heat_pct

    def calculate_heat(
        self,
        open_positions: List[Position],
        portfolio_value: float
    ) -> Tuple[float, str]:
        """
        Calculate current portfolio heat

        Args:
            open_positions: List of open positions
            portfolio_value: Total portfolio value

        Returns:
            (heat_pct, action) tuple
            heat_pct: Current heat as % of portfolio
            action: 'STOP_TRADING', 'REDUCE_SIZE', or 'NORMAL'
        """
        try:
            if not open_positions:
                return 0.0, 'NORMAL'

            # Calculate risk for each position
            total_risk = 0.0
            for pos in open_positions:
                position_risk = abs(pos.entry_price - pos.stop_loss) * pos.shares
                total_risk += position_risk

            # Calculate heat percentage
            heat_pct = total_risk / portfolio_value if portfolio_value > 0 else 0

            # Determine action
            if heat_pct >= self.max_heat_pct:
                action = 'STOP_TRADING'
                self.logger.warning(
                    f"Portfolio heat {heat_pct:.2%} exceeds maximum {self.max_heat_pct:.2%}. "
                    f"Stop taking new positions!"
                )
            elif heat_pct >= self.warning_heat_pct:
                action = 'REDUCE_SIZE'
                self.logger.warning(
                    f"Portfolio heat {heat_pct:.2%} exceeds warning {self.warning_heat_pct:.2%}. "
                    f"Reducing new position sizes."
                )
            else:
                action = 'NORMAL'
                self.logger.info(f"Portfolio heat: {heat_pct:.2%} - Normal trading")

            return heat_pct, action

        except Exception as e:
            self.logger.error(f"Error calculating portfolio heat: {e}")
            return 0.0, 'NORMAL'

    def adjust_position_size(
        self,
        proposed_size: float,
        current_heat: float,
        portfolio_value: float,
        new_position_risk: float
    ) -> float:
        """
        Adjust position size based on current heat

        Args:
            proposed_size: Proposed position size in dollars
            current_heat: Current portfolio heat (0.0 to 1.0)
            portfolio_value: Total portfolio value
            new_position_risk: Risk of new position in dollars

        Returns:
            Adjusted position size in dollars
        """
        try:
            # Calculate what heat would be after adding this position
            new_heat = current_heat + (new_position_risk / portfolio_value)

            if new_heat >= self.max_heat_pct:
                # Would exceed max heat - don't trade
                self.logger.warning(
                    f"Position would increase heat to {new_heat:.2%}. "
                    f"Rejecting position."
                )
                return 0.0

            elif new_heat >= self.warning_heat_pct:
                # Would exceed warning - reduce size by 50%
                adjusted_size = proposed_size * 0.5
                self.logger.info(
                    f"Reducing position size by 50% due to heat: "
                    f"${proposed_size:.2f} → ${adjusted_size:.2f}"
                )
                return adjusted_size

            else:
                # Normal trading
                return proposed_size

        except Exception as e:
            self.logger.error(f"Error adjusting position size: {e}")
            return proposed_size


class AdvancedPositionSizer:
    """
    Unified position sizing system combining multiple methods
    """

    def __init__(
        self,
        portfolio_value: float,
        default_method: PositionSizeMethod = PositionSizeMethod.VOLATILITY_ADJUSTED
    ):
        """
        Args:
            portfolio_value: Total portfolio value
            default_method: Default position sizing method
        """
        self.logger = logging.getLogger(__name__)
        self.portfolio_value = portfolio_value
        self.default_method = default_method

        # Initialize calculators
        self.kelly_calculator = KellyCriterionCalculator(fraction=0.5)
        self.volatility_sizer = VolatilityAdjustedSizing(risk_per_trade_pct=0.01)
        self.heat_manager = PortfolioHeatManager()

    def calculate_position_size(
        self,
        symbol: str,
        price: float,
        stop_loss: float,
        atr: float,
        method: Optional[PositionSizeMethod] = None,
        win_rate: Optional[float] = None,
        reward_risk_ratio: Optional[float] = None,
        open_positions: Optional[List[Position]] = None
    ) -> PositionSize:
        """
        Calculate position size using specified method

        Args:
            symbol: Stock symbol
            price: Current price
            stop_loss: Stop loss price
            atr: Average True Range
            method: Position sizing method (or use default)
            win_rate: Historical win rate (for Kelly)
            reward_risk_ratio: Average win/loss ratio (for Kelly)
            open_positions: Current open positions (for heat management)

        Returns:
            PositionSize object with calculated size and reasoning
        """
        try:
            method = method or self.default_method
            open_positions = open_positions or []

            # Calculate shares based on method
            if method == PositionSizeMethod.KELLY_CRITERION:
                shares = self._kelly_method(price, win_rate, reward_risk_ratio)
                reasoning = f"Kelly Criterion (win_rate={win_rate:.1%}, R:R={reward_risk_ratio:.1f})"

            elif method == PositionSizeMethod.VOLATILITY_ADJUSTED:
                shares = self._volatility_method(price, atr, stop_loss)
                reasoning = f"Volatility-adjusted (ATR=${atr:.2f}, risk=1%)"

            elif method == PositionSizeMethod.FIXED_PERCENT:
                shares = self._fixed_percent_method(price, percent=0.10)
                reasoning = "Fixed 10% of portfolio"

            elif method == PositionSizeMethod.FIXED_DOLLAR:
                shares = self._fixed_dollar_method(price, amount=10000)
                reasoning = "Fixed $10,000 position"

            else:
                shares = self._volatility_method(price, atr, stop_loss)
                reasoning = "Default volatility-adjusted"

            # Calculate dollar amount
            dollar_amount = shares * price
            percent_of_portfolio = dollar_amount / self.portfolio_value

            # Calculate risk amount
            risk_per_share = abs(price - stop_loss)
            risk_amount = risk_per_share * shares

            # Check portfolio heat
            current_heat, heat_action = self.heat_manager.calculate_heat(
                open_positions, self.portfolio_value
            )

            # Adjust for portfolio heat
            if heat_action == 'STOP_TRADING':
                shares = 0
                dollar_amount = 0
                reasoning += " | BLOCKED: Portfolio heat too high"
            elif heat_action == 'REDUCE_SIZE':
                shares = shares // 2
                dollar_amount = shares * price
                risk_amount = risk_per_share * shares
                reasoning += " | REDUCED: High portfolio heat"

            return PositionSize(
                shares=shares,
                dollar_amount=dollar_amount,
                percent_of_portfolio=percent_of_portfolio,
                risk_amount=risk_amount,
                method=method,
                reasoning=reasoning
            )

        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            # Return minimum safe position
            return PositionSize(
                shares=1,
                dollar_amount=price,
                percent_of_portfolio=price / self.portfolio_value,
                risk_amount=abs(price - stop_loss),
                method=method or self.default_method,
                reasoning=f"Error: {str(e)} - using minimum size"
            )

    def _kelly_method(
        self,
        price: float,
        win_rate: Optional[float],
        reward_risk_ratio: Optional[float]
    ) -> int:
        """Calculate shares using Kelly Criterion"""
        if win_rate is None or reward_risk_ratio is None:
            # Default to 10% position if no stats available
            return int((self.portfolio_value * 0.10) / price)

        dollar_amount = self.kelly_calculator.calculate_position_size(
            win_rate, reward_risk_ratio, self.portfolio_value
        )
        return int(dollar_amount / price)

    def _volatility_method(
        self,
        price: float,
        atr: float,
        stop_loss: float
    ) -> int:
        """Calculate shares using volatility-adjusted method"""
        return self.volatility_sizer.calculate_shares(
            price, atr, self.portfolio_value
        )

    def _fixed_percent_method(self, price: float, percent: float = 0.10) -> int:
        """Calculate shares using fixed percentage of portfolio"""
        dollar_amount = self.portfolio_value * percent
        return int(dollar_amount / price)

    def _fixed_dollar_method(self, price: float, amount: float = 10000) -> int:
        """Calculate shares using fixed dollar amount"""
        return int(amount / price)

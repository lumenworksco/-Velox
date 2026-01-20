"""Strategy signal generation logic for all trading strategies"""

import pandas as pd
import numpy as np
import logging
from typing import Literal, Optional, Dict, Any
from core.indicators import TechnicalIndicators

logger = logging.getLogger(__name__)

Signal = Literal['BUY', 'SELL', 'HOLD']


class StrategyLogic:
    """Generate trading signals for all strategies"""

    def __init__(self):
        self.indicators = TechnicalIndicators()

    def generate_signal(
        self,
        strategy_id: str,
        symbol: str,
        data: pd.DataFrame,
        parameters: Dict[str, Any]
    ) -> Signal:
        """
        Generate trading signal based on strategy type

        Args:
            strategy_id: Strategy identifier (e.g., 'ma_crossover')
            symbol: Stock symbol
            data: Historical price data with OHLCV columns
            parameters: Strategy-specific parameters

        Returns:
            'BUY', 'SELL', or 'HOLD'
        """
        try:
            # Ensure we have enough data
            if data is None or len(data) < 50:
                logger.warning(f"Insufficient data for {symbol}, need at least 50 bars")
                return 'HOLD'

            # Route to appropriate strategy
            if strategy_id == 'ma_crossover':
                return self._ma_crossover_signal(data, parameters)
            elif strategy_id == 'rsi_mean_reversion':
                return self._rsi_mean_reversion_signal(data, parameters)
            elif strategy_id == 'momentum':
                return self._momentum_signal(data, parameters)
            elif strategy_id == 'mean_reversion':
                return self._mean_reversion_signal(data, parameters)
            elif strategy_id == 'quick_test':
                return self._quick_test_signal(data, parameters)
            elif strategy_id == 'multi_timeframe':
                return self._multi_timeframe_signal(data, parameters)
            elif strategy_id == 'volatility_breakout':
                return self._volatility_breakout_signal(data, parameters)
            else:
                logger.warning(f"Unknown strategy: {strategy_id}")
                return 'HOLD'

        except Exception as e:
            logger.error(f"Error generating signal for {strategy_id} on {symbol}: {e}")
            return 'HOLD'

    def _ma_crossover_signal(self, data: pd.DataFrame, params: Dict) -> Signal:
        """Moving Average Crossover Strategy"""
        fast_period = params.get('fast_period', 10)
        slow_period = params.get('slow_period', 30)

        # Calculate moving averages
        fast_ma = data['close'].rolling(window=fast_period).mean()
        slow_ma = data['close'].rolling(window=slow_period).mean()

        # Current and previous values
        fast_current = fast_ma.iloc[-1]
        slow_current = slow_ma.iloc[-1]
        fast_prev = fast_ma.iloc[-2]
        slow_prev = slow_ma.iloc[-2]

        # Check for crossover
        if fast_prev <= slow_prev and fast_current > slow_current:
            # Golden cross - buy signal
            logger.info(f"MA Crossover: BUY signal (fast={fast_current:.2f} > slow={slow_current:.2f})")
            return 'BUY'
        elif fast_prev >= slow_prev and fast_current < slow_current:
            # Death cross - sell signal
            logger.info(f"MA Crossover: SELL signal (fast={fast_current:.2f} < slow={slow_current:.2f})")
            return 'SELL'
        else:
            return 'HOLD'

    def _rsi_mean_reversion_signal(self, data: pd.DataFrame, params: Dict) -> Signal:
        """RSI Mean Reversion Strategy"""
        rsi_period = params.get('rsi_period', 14)
        oversold = params.get('oversold', 30)
        overbought = params.get('overbought', 70)

        # Calculate RSI
        rsi = self.indicators.calculate_rsi(data, period=rsi_period)
        current_rsi = rsi.iloc[-1]

        if current_rsi < oversold:
            logger.info(f"RSI Mean Reversion: BUY signal (RSI={current_rsi:.2f} < {oversold})")
            return 'BUY'
        elif current_rsi > overbought:
            logger.info(f"RSI Mean Reversion: SELL signal (RSI={current_rsi:.2f} > {overbought})")
            return 'SELL'
        else:
            return 'HOLD'

    def _momentum_signal(self, data: pd.DataFrame, params: Dict) -> Signal:
        """Momentum Strategy - Follow strong price trends"""
        lookback_period = params.get('lookback_period', 20)
        momentum_threshold = params.get('momentum_threshold', 0.02)  # 2%

        # Calculate momentum (rate of change)
        if len(data) < lookback_period:
            return 'HOLD'

        current_price = data['close'].iloc[-1]
        past_price = data['close'].iloc[-lookback_period]
        momentum = (current_price - past_price) / past_price

        # Check if momentum is strong enough
        if momentum > momentum_threshold:
            logger.info(f"Momentum: BUY signal (momentum={momentum*100:.2f}% > {momentum_threshold*100}%)")
            return 'BUY'
        elif momentum < -momentum_threshold:
            logger.info(f"Momentum: SELL signal (momentum={momentum*100:.2f}% < -{momentum_threshold*100}%)")
            return 'SELL'
        else:
            return 'HOLD'

    def _mean_reversion_signal(self, data: pd.DataFrame, params: Dict) -> Signal:
        """Mean Reversion Strategy - Fade extreme moves"""
        z_score_threshold = params.get('z_score_threshold', 2.0)
        lookback_period = params.get('lookback_period', 20)

        if len(data) < lookback_period:
            return 'HOLD'

        # Calculate z-score
        closes = data['close'].iloc[-lookback_period:]
        mean_price = closes.mean()
        std_price = closes.std()

        if std_price == 0:
            return 'HOLD'

        current_price = data['close'].iloc[-1]
        z_score = (current_price - mean_price) / std_price

        # Extreme deviations signal mean reversion
        if z_score < -z_score_threshold:
            # Price is way below mean - expect reversion up
            logger.info(f"Mean Reversion: BUY signal (z-score={z_score:.2f} < -{z_score_threshold})")
            return 'BUY'
        elif z_score > z_score_threshold:
            # Price is way above mean - expect reversion down
            logger.info(f"Mean Reversion: SELL signal (z-score={z_score:.2f} > {z_score_threshold})")
            return 'SELL'
        else:
            return 'HOLD'

    def _quick_test_signal(self, data: pd.DataFrame, params: Dict) -> Signal:
        """Quick Test Strategy - Fast executing test strategy"""
        threshold = params.get('threshold', 0.001)  # 0.1%

        if len(data) < 2:
            return 'HOLD'

        # Simple price change strategy
        current_price = data['close'].iloc[-1]
        prev_price = data['close'].iloc[-2]
        change = (current_price - prev_price) / prev_price

        if change > threshold:
            logger.info(f"Quick Test: BUY signal (change={change*100:.2f}% > {threshold*100}%)")
            return 'BUY'
        elif change < -threshold:
            logger.info(f"Quick Test: SELL signal (change={change*100:.2f}% < -{threshold*100}%)")
            return 'SELL'
        else:
            return 'HOLD'

    def _multi_timeframe_signal(self, data: pd.DataFrame, params: Dict) -> Signal:
        """
        Multi-Timeframe Confluence Strategy
        Analyzes multiple timeframes and only trades when they align
        """
        min_alignment = params.get('min_alignment', 0.66)  # 66% alignment required
        confidence_threshold = params.get('confidence_threshold', 0.70)

        # For simplicity, we'll use different MA periods to simulate timeframes
        # In production, you'd fetch actual hourly/5min data

        # Daily trend (slow MA)
        daily_ma = data['close'].rolling(window=50).mean()
        daily_signal = 1 if data['close'].iloc[-1] > daily_ma.iloc[-1] else -1

        # Hourly trend (medium MA)
        hourly_ma = data['close'].rolling(window=20).mean()
        hourly_signal = 1 if data['close'].iloc[-1] > hourly_ma.iloc[-1] else -1

        # Intraday trend (fast MA)
        intraday_ma = data['close'].rolling(window=5).mean()
        intraday_signal = 1 if data['close'].iloc[-1] > intraday_ma.iloc[-1] else -1

        # Calculate alignment
        signals = [daily_signal, hourly_signal, intraday_signal]
        bullish_count = sum(1 for s in signals if s > 0)
        bearish_count = sum(1 for s in signals if s < 0)

        bullish_alignment = bullish_count / len(signals)
        bearish_alignment = bearish_count / len(signals)

        # Only trade when alignment is strong
        if bullish_alignment >= min_alignment:
            logger.info(f"Multi-Timeframe: BUY signal ({bullish_alignment*100:.0f}% bullish alignment)")
            return 'BUY'
        elif bearish_alignment >= min_alignment:
            logger.info(f"Multi-Timeframe: SELL signal ({bearish_alignment*100:.0f}% bearish alignment)")
            return 'SELL'
        else:
            logger.debug(f"Multi-Timeframe: HOLD (alignment insufficient)")
            return 'HOLD'

    def _volatility_breakout_signal(self, data: pd.DataFrame, params: Dict) -> Signal:
        """
        Volatility Breakout Strategy
        ATR-based breakout detection with volume confirmation
        """
        atr_period = params.get('atr_period', 14)
        breakout_multiplier = params.get('breakout_multiplier', 2.0)
        volume_confirmation = params.get('volume_confirmation', True)

        if len(data) < atr_period + 1:
            return 'HOLD'

        # Calculate ATR
        atr = self.indicators.calculate_atr(data, period=atr_period)
        current_atr = atr.iloc[-1]

        # Calculate recent high/low
        lookback = 20
        recent_high = data['high'].iloc[-lookback:].max()
        recent_low = data['low'].iloc[-lookback:].max()

        current_price = data['close'].iloc[-1]
        prev_price = data['close'].iloc[-2]

        # Breakout levels
        upper_breakout = recent_high + (current_atr * breakout_multiplier)
        lower_breakout = recent_low - (current_atr * breakout_multiplier)

        # Volume confirmation
        if volume_confirmation and 'volume' in data.columns:
            avg_volume = data['volume'].iloc[-20:].mean()
            current_volume = data['volume'].iloc[-1]
            volume_surge = current_volume > avg_volume * 1.5
        else:
            volume_surge = True  # Skip if no volume data

        # Check for breakouts
        if current_price > upper_breakout and prev_price <= upper_breakout:
            if volume_surge or not volume_confirmation:
                logger.info(f"Volatility Breakout: BUY signal (price={current_price:.2f} > breakout={upper_breakout:.2f})")
                return 'BUY'

        if current_price < lower_breakout and prev_price >= lower_breakout:
            if volume_surge or not volume_confirmation:
                logger.info(f"Volatility Breakout: SELL signal (price={current_price:.2f} < breakout={lower_breakout:.2f})")
                return 'SELL'

        return 'HOLD'


# Global instance
strategy_logic = StrategyLogic()

"""
Advanced Trading Strategies for AlphaFlow
Institutional-grade algorithms with multi-timeframe analysis, regime detection, and ensemble methods
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass
from enum import Enum

from .config import TradingConfig
from .data_structures import TradeSignal, SignalAction
from .indicators import AdvancedIndicators


class MarketRegime(Enum):
    """Market regime classification"""
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGING = "ranging"
    VOLATILE = "volatile"
    QUIET = "quiet"
    MIXED = "mixed"


class VolumeConfirmation(Enum):
    """Volume analysis results"""
    STRONG_CONFIRMATION = "strong_confirmation"
    WEAK_SIGNAL = "weak_signal"
    NORMAL = "normal"
    DIVERGENCE = "divergence"


@dataclass
class MultiTimeframeSignal:
    """Signal from multi-timeframe analysis"""
    symbol: str
    action: SignalAction
    confidence: float
    timeframe_alignment: float  # 0.0 to 1.0 (how aligned timeframes are)
    daily_trend: str
    hourly_momentum: str
    entry_timing: str
    volume_confirmation: VolumeConfirmation
    regime: MarketRegime
    reasoning: str
    price: float
    stop_loss: float
    take_profit: float


class MarketRegimeDetector:
    """Detect and classify market conditions"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def detect_regime(self, df: pd.DataFrame) -> Tuple[MarketRegime, float]:
        """
        Detect market regime using ADX, ATR, and price action

        Returns:
            (regime, confidence) tuple
        """
        try:
            # Get indicators
            adx = df['adx'].iloc[-1] if 'adx' in df.columns else 20
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else df['close'].iloc[-1] * 0.015
            close = df['close'].iloc[-1]

            # Calculate ATR percentile (volatility ranking)
            atr_percentile = self._calculate_percentile(df['atr'], atr) if 'atr' in df.columns else 0.5

            # Calculate trend slope
            prices = df['close'].tail(20).values
            x = np.arange(len(prices))
            slope = np.polyfit(x, prices, 1)[0]
            normalized_slope = slope / close  # Normalize by price

            # Determine regime
            if adx > 25:  # Strong trend
                if normalized_slope > 0.001:
                    regime = MarketRegime.TRENDING_UP
                    confidence = min(0.95, adx / 50)
                elif normalized_slope < -0.001:
                    regime = MarketRegime.TRENDING_DOWN
                    confidence = min(0.95, adx / 50)
                else:
                    regime = MarketRegime.MIXED
                    confidence = 0.5
            elif adx < 15:  # Weak trend = ranging
                regime = MarketRegime.RANGING
                confidence = min(0.9, (25 - adx) / 25)
            else:  # Mixed conditions
                regime = MarketRegime.MIXED
                confidence = 0.5

            # Overlay volatility assessment
            if atr_percentile > 0.8:
                regime = MarketRegime.VOLATILE
                confidence = atr_percentile
            elif atr_percentile < 0.2:
                regime = MarketRegime.QUIET
                confidence = 1.0 - atr_percentile

            return regime, confidence

        except Exception as e:
            self.logger.error(f"Error detecting market regime: {e}")
            return MarketRegime.MIXED, 0.5

    def _calculate_percentile(self, series: pd.Series, value: float) -> float:
        """Calculate what percentile a value is in a series"""
        if len(series) < 100:
            return 0.5
        return (series.tail(100) < value).sum() / 100


class VolumeAnalyzer:
    """Analyze volume patterns for signal confirmation"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_volume(self, df: pd.DataFrame) -> Tuple[VolumeConfirmation, float]:
        """
        Analyze volume for trade confirmation

        Returns:
            (confirmation_level, strength) tuple
        """
        try:
            if 'volume' not in df.columns or len(df) < 20:
                return VolumeConfirmation.NORMAL, 0.5

            current_volume = df['volume'].iloc[-1]
            avg_volume = df['volume'].rolling(20).mean().iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0

            # Price change
            price_change = df['close'].pct_change().iloc[-1]

            # Volume trend (increasing/decreasing)
            volume_trend = self._calculate_volume_trend(df['volume'].tail(10))

            # Classify
            if volume_ratio > 1.5:
                # High volume
                if abs(price_change) > 0.015:  # 1.5% move
                    return VolumeConfirmation.STRONG_CONFIRMATION, min(0.95, volume_ratio / 2)
                else:
                    # High volume but small price move = potential reversal
                    return VolumeConfirmation.DIVERGENCE, 0.7
            elif volume_ratio < 0.5:
                # Low volume
                return VolumeConfirmation.WEAK_SIGNAL, 0.3
            else:
                # Normal volume
                return VolumeConfirmation.NORMAL, 0.6

        except Exception as e:
            self.logger.error(f"Error analyzing volume: {e}")
            return VolumeConfirmation.NORMAL, 0.5

    def _calculate_volume_trend(self, volume_series: pd.Series) -> float:
        """Calculate volume trend slope"""
        if len(volume_series) < 5:
            return 0.0
        x = np.arange(len(volume_series))
        slope = np.polyfit(x, volume_series.values, 1)[0]
        return slope


class MultiTimeframeStrategy:
    """
    Advanced multi-timeframe strategy with regime detection

    Analyzes multiple timeframes:
    - Daily: Overall trend direction
    - Hourly: Momentum confirmation (if available)
    - 5-min/Entry: Precise entry timing (if available)

    Only generates signals when timeframes align
    """

    def __init__(self, data_fetcher=None):
        self.logger = logging.getLogger(__name__)
        self.data_fetcher = data_fetcher
        self.regime_detector = MarketRegimeDetector()
        self.volume_analyzer = VolumeAnalyzer()
        self.indicators = AdvancedIndicators()

    def generate_signal(
        self,
        df_daily: pd.DataFrame,
        symbol: str,
        df_hourly: Optional[pd.DataFrame] = None,
        df_5min: Optional[pd.DataFrame] = None
    ) -> Optional[MultiTimeframeSignal]:
        """
        Generate signal with multi-timeframe analysis

        Args:
            df_daily: Daily timeframe data (required)
            symbol: Stock symbol
            df_hourly: Hourly timeframe data (optional)
            df_5min: 5-minute timeframe data (optional)

        Returns:
            MultiTimeframeSignal or None
        """
        try:
            if df_daily is None or len(df_daily) < 50:
                return None

            # 1. Detect market regime
            regime, regime_confidence = self.regime_detector.detect_regime(df_daily)

            # 2. Analyze volume
            volume_conf, volume_strength = self.volume_analyzer.analyze_volume(df_daily)

            # 3. Get daily trend
            daily_trend = self._analyze_daily_trend(df_daily)

            # 4. Get hourly momentum (if available)
            if df_hourly is not None and len(df_hourly) >= 20:
                hourly_momentum = self._analyze_hourly_momentum(df_hourly)
            else:
                hourly_momentum = "NEUTRAL"

            # 5. Get entry timing (if 5-min data available)
            if df_5min is not None and len(df_5min) >= 20:
                entry_timing = self._analyze_entry_timing(df_5min)
            else:
                entry_timing = "NEUTRAL"

            # 6. Calculate timeframe alignment
            alignment_score = self._calculate_alignment(
                daily_trend, hourly_momentum, entry_timing
            )

            # 7. Determine action based on alignment
            if alignment_score < 0.6:
                # Not enough alignment
                return None

            # Determine action
            action, confidence = self._determine_action(
                daily_trend=daily_trend,
                hourly_momentum=hourly_momentum,
                entry_timing=entry_timing,
                regime=regime,
                volume_conf=volume_conf,
                alignment_score=alignment_score,
                regime_confidence=regime_confidence,
                volume_strength=volume_strength
            )

            if action == SignalAction.HOLD or confidence < 0.6:
                return None

            # 8. Calculate stop loss and take profit
            current_price = df_daily['close'].iloc[-1]
            atr = df_daily['atr'].iloc[-1] if 'atr' in df_daily.columns else current_price * 0.02

            if action in [SignalAction.BUY, SignalAction.STRONG_BUY]:
                stop_loss = current_price - (2.5 * atr)  # Wider stop for MTF
                take_profit = current_price + (4 * atr)   # Better R:R
            else:
                stop_loss = current_price + (2.5 * atr)
                take_profit = current_price - (4 * atr)

            # 9. Build reasoning
            reasoning = self._build_reasoning(
                daily_trend, hourly_momentum, entry_timing,
                regime, volume_conf, alignment_score
            )

            return MultiTimeframeSignal(
                symbol=symbol,
                action=action,
                confidence=confidence,
                timeframe_alignment=alignment_score,
                daily_trend=daily_trend,
                hourly_momentum=hourly_momentum,
                entry_timing=entry_timing,
                volume_confirmation=volume_conf,
                regime=regime,
                reasoning=reasoning,
                price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit
            )

        except Exception as e:
            self.logger.error(f"Error in multi-timeframe strategy: {e}")
            return None

    def _analyze_daily_trend(self, df: pd.DataFrame) -> str:
        """Analyze daily trend using multiple indicators"""
        try:
            # Moving averages
            sma_20 = df['sma_20'].iloc[-1] if 'sma_20' in df.columns else df['close'].rolling(20).mean().iloc[-1]
            sma_50 = df['sma_50'].iloc[-1] if 'sma_50' in df.columns else df['close'].rolling(50).mean().iloc[-1]
            price = df['close'].iloc[-1]

            # ADX for trend strength
            adx = df['adx'].iloc[-1] if 'adx' in df.columns else 20

            # Determine trend
            if price > sma_20 > sma_50 and adx > 20:
                return "STRONG_UP"
            elif price > sma_20 and adx > 15:
                return "UP"
            elif price < sma_20 < sma_50 and adx > 20:
                return "STRONG_DOWN"
            elif price < sma_20 and adx > 15:
                return "DOWN"
            else:
                return "NEUTRAL"

        except Exception as e:
            self.logger.error(f"Error analyzing daily trend: {e}")
            return "NEUTRAL"

    def _analyze_hourly_momentum(self, df: pd.DataFrame) -> str:
        """Analyze hourly momentum"""
        try:
            rsi = df['rsi'].iloc[-1] if 'rsi' in df.columns else 50
            macd = df['macd'].iloc[-1] if 'macd' in df.columns else 0
            macd_signal = df['macd_signal'].iloc[-1] if 'macd_signal' in df.columns else 0

            # Momentum score
            score = 0

            if rsi > 60:
                score += 1
            elif rsi < 40:
                score -= 1

            if macd > macd_signal and macd > 0:
                score += 2
            elif macd < macd_signal and macd < 0:
                score -= 2

            if score >= 2:
                return "STRONG_BULLISH"
            elif score == 1:
                return "BULLISH"
            elif score <= -2:
                return "STRONG_BEARISH"
            elif score == -1:
                return "BEARISH"
            else:
                return "NEUTRAL"

        except Exception as e:
            self.logger.error(f"Error analyzing hourly momentum: {e}")
            return "NEUTRAL"

    def _analyze_entry_timing(self, df: pd.DataFrame) -> str:
        """Analyze 5-min timeframe for entry timing"""
        try:
            # Recent price action
            close_prices = df['close'].tail(12).values  # Last hour (12 x 5min)
            current_price = close_prices[-1]
            avg_price = close_prices.mean()

            # Short-term momentum
            rsi_5min = df['rsi'].iloc[-1] if 'rsi' in df.columns else 50

            # Determine timing
            if current_price > avg_price and rsi_5min > 45 and rsi_5min < 70:
                return "BUY_NOW"
            elif current_price < avg_price and rsi_5min < 55 and rsi_5min > 30:
                return "SELL_NOW"
            elif rsi_5min < 30:
                return "WAIT_OVERSOLD"
            elif rsi_5min > 70:
                return "WAIT_OVERBOUGHT"
            else:
                return "NEUTRAL"

        except Exception as e:
            self.logger.error(f"Error analyzing entry timing: {e}")
            return "NEUTRAL"

    def _calculate_alignment(self, daily: str, hourly: str, entry: str) -> float:
        """Calculate how aligned the timeframes are (0.0 to 1.0)"""
        bullish_terms = ["STRONG_UP", "UP", "STRONG_BULLISH", "BULLISH", "BUY_NOW"]
        bearish_terms = ["STRONG_DOWN", "DOWN", "STRONG_BEARISH", "BEARISH", "SELL_NOW"]

        signals = [daily, hourly, entry]

        # Count bullish and bearish signals
        bullish_count = sum(1 for s in signals if s in bullish_terms)
        bearish_count = sum(1 for s in signals if s in bearish_terms)

        # Maximum alignment is when all 3 agree
        max_alignment = max(bullish_count, bearish_count)

        return max_alignment / 3.0

    def _determine_action(
        self,
        daily_trend: str,
        hourly_momentum: str,
        entry_timing: str,
        regime: MarketRegime,
        volume_conf: VolumeConfirmation,
        alignment_score: float,
        regime_confidence: float,
        volume_strength: float
    ) -> Tuple[SignalAction, float]:
        """Determine final action and confidence"""

        bullish = ["STRONG_UP", "UP", "STRONG_BULLISH", "BULLISH", "BUY_NOW"]
        bearish = ["STRONG_DOWN", "DOWN", "STRONG_BEARISH", "BEARISH", "SELL_NOW"]

        # Base confidence from alignment
        base_confidence = alignment_score

        # Adjust for regime
        if regime == MarketRegime.TRENDING_UP and daily_trend in bullish:
            base_confidence *= 1.2
        elif regime == MarketRegime.TRENDING_DOWN and daily_trend in bearish:
            base_confidence *= 1.2
        elif regime == MarketRegime.RANGING:
            # Reduce confidence in ranging markets
            base_confidence *= 0.8

        # Adjust for volume
        if volume_conf == VolumeConfirmation.STRONG_CONFIRMATION:
            base_confidence *= 1.15
        elif volume_conf == VolumeConfirmation.WEAK_SIGNAL:
            base_confidence *= 0.7
        elif volume_conf == VolumeConfirmation.DIVERGENCE:
            # Volume divergence reduces confidence
            base_confidence *= 0.6

        # Determine action
        if daily_trend in bullish and alignment_score >= 0.66:
            if daily_trend == "STRONG_UP" and alignment_score >= 0.85:
                action = SignalAction.STRONG_BUY
            else:
                action = SignalAction.BUY
        elif daily_trend in bearish and alignment_score >= 0.66:
            if daily_trend == "STRONG_DOWN" and alignment_score >= 0.85:
                action = SignalAction.STRONG_SELL
            else:
                action = SignalAction.SELL
        else:
            action = SignalAction.HOLD

        # Cap confidence
        final_confidence = min(0.95, base_confidence)

        return action, final_confidence

    def _build_reasoning(
        self,
        daily_trend: str,
        hourly_momentum: str,
        entry_timing: str,
        regime: MarketRegime,
        volume_conf: VolumeConfirmation,
        alignment: float
    ) -> str:
        """Build human-readable reasoning"""
        parts = [
            f"MTF Alignment: {alignment:.0%}",
            f"Daily: {daily_trend}",
            f"Hourly: {hourly_momentum}",
            f"Entry: {entry_timing}",
            f"Regime: {regime.value}",
            f"Volume: {volume_conf.value}"
        ]
        return " | ".join(parts)

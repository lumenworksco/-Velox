"""Trading strategies for Version 6 Trading App."""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import List, Optional

from .config import TradingConfig, SENTIMENT_AVAILABLE
from .data_structures import TradeSignal, SignalAction
from .ml_predictor import MLPredictor
from .indicators import AdvancedIndicators


class TradingStrategies:
    """Collection of trading strategies."""
    
    def __init__(self, ml_predictor: Optional[MLPredictor] = None):
        self.logger = logging.getLogger(__name__)
        self.ml_predictor = ml_predictor or MLPredictor()
    
    def generate_all_signals(self, df: pd.DataFrame, symbol: str) -> List[TradeSignal]:
        """Generate signals from all strategies."""
        
        signals = []
        
        # Technical signals
        tech_signal = self.technical_momentum_strategy(df, symbol)
        if tech_signal:
            signals.append(tech_signal)
        
        # Mean reversion signals
        mr_signal = self.mean_reversion_strategy(df, symbol)
        if mr_signal:
            signals.append(mr_signal)
        
        # ML-based signals
        if self.ml_predictor and self.ml_predictor.is_trained:
            ml_signal = self.ml_strategy(df, symbol)
            if ml_signal:
                signals.append(ml_signal)
        
        # Trend following signals
        trend_signal = self.trend_following_strategy(df, symbol)
        if trend_signal:
            signals.append(trend_signal)
        
        return signals
    
    def technical_momentum_strategy(self, df: pd.DataFrame, symbol: str) -> Optional[TradeSignal]:
        """Momentum strategy using RSI, MACD, and Stochastic."""
        
        if df is None or len(df) < 50:
            return None
        
        try:
            current_price = df['close'].iloc[-1]
            
            # Get indicators
            rsi = df['rsi'].iloc[-1] if 'rsi' in df.columns else 50
            macd = df['macd'].iloc[-1] if 'macd' in df.columns else 0
            macd_signal = df['macd_signal'].iloc[-1] if 'macd_signal' in df.columns else 0
            stoch_k = df['stoch_k'].iloc[-1] if 'stoch_k' in df.columns else 50
            
            # Check for NaN
            if any(pd.isna([rsi, macd, macd_signal, stoch_k])):
                return None
            
            # Calculate signal
            buy_score = 0
            sell_score = 0
            
            # RSI signals
            if rsi < TradingConfig.RSI_OVERSOLD:
                buy_score += 2
            elif rsi > TradingConfig.RSI_OVERBOUGHT:
                sell_score += 2
            elif rsi < 40:
                buy_score += 1
            elif rsi > 60:
                sell_score += 1
            
            # MACD signals
            if macd > macd_signal and macd > 0:
                buy_score += 2
            elif macd < macd_signal and macd < 0:
                sell_score += 2
            elif macd > macd_signal:
                buy_score += 1
            elif macd < macd_signal:
                sell_score += 1
            
            # Stochastic signals
            if stoch_k < 20:
                buy_score += 1
            elif stoch_k > 80:
                sell_score += 1
            
            # Determine action
            if buy_score >= 4:
                action = SignalAction.STRONG_BUY
                confidence = min(0.9, 0.5 + buy_score * 0.08)
            elif buy_score >= 3:
                action = SignalAction.BUY
                confidence = min(0.8, 0.4 + buy_score * 0.08)
            elif sell_score >= 4:
                action = SignalAction.STRONG_SELL
                confidence = min(0.9, 0.5 + sell_score * 0.08)
            elif sell_score >= 3:
                action = SignalAction.SELL
                confidence = min(0.8, 0.4 + sell_score * 0.08)
            else:
                return None
            
            # Calculate stop loss and take profit
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else current_price * 0.02
            if pd.isna(atr):
                atr = current_price * 0.02
            
            if action in [SignalAction.BUY, SignalAction.STRONG_BUY]:
                stop_loss = current_price - (2 * atr)
                take_profit = current_price + (3 * atr)
            else:
                stop_loss = current_price + (2 * atr)
                take_profit = current_price - (3 * atr)
            
            return TradeSignal(
                symbol=symbol,
                action=action,
                confidence=confidence,
                strategy="Technical Momentum",
                price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                reasoning=f"RSI: {rsi:.1f}, MACD: {macd:.4f}, Stoch: {stoch_k:.1f}"
            )
            
        except Exception as e:
            self.logger.error(f"Error in technical momentum strategy: {e}")
            return None
    
    def mean_reversion_strategy(self, df: pd.DataFrame, symbol: str) -> Optional[TradeSignal]:
        """Mean reversion using Bollinger Bands."""
        
        if df is None or len(df) < 50:
            return None
        
        try:
            current_price = df['close'].iloc[-1]
            
            # Get Bollinger Band values
            bb_upper = df['bb_upper'].iloc[-1] if 'bb_upper' in df.columns else None
            bb_lower = df['bb_lower'].iloc[-1] if 'bb_lower' in df.columns else None
            bb_percent = df['bb_percent'].iloc[-1] if 'bb_percent' in df.columns else None
            
            if any(pd.isna([bb_upper, bb_lower, bb_percent])):
                return None
            
            # Check for extreme positions
            if bb_percent < 0.05:  # Near lower band
                action = SignalAction.BUY
                confidence = min(0.8, 0.5 + (0.1 - bb_percent) * 5)
                reasoning = f"Price near lower BB ({bb_percent:.1%})"
            elif bb_percent > 0.95:  # Near upper band
                action = SignalAction.SELL
                confidence = min(0.8, 0.5 + (bb_percent - 0.9) * 5)
                reasoning = f"Price near upper BB ({bb_percent:.1%})"
            else:
                return None
            
            # Calculate stop loss and take profit
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else current_price * 0.02
            if pd.isna(atr):
                atr = current_price * 0.02
            
            if action == SignalAction.BUY:
                stop_loss = current_price - (1.5 * atr)
                take_profit = df['bb_middle'].iloc[-1] if 'bb_middle' in df.columns else current_price * 1.02
            else:
                stop_loss = current_price + (1.5 * atr)
                take_profit = df['bb_middle'].iloc[-1] if 'bb_middle' in df.columns else current_price * 0.98
            
            return TradeSignal(
                symbol=symbol,
                action=action,
                confidence=confidence,
                strategy="Mean Reversion",
                price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                reasoning=reasoning
            )
            
        except Exception as e:
            self.logger.error(f"Error in mean reversion strategy: {e}")
            return None
    
    def ml_strategy(self, df: pd.DataFrame, symbol: str) -> Optional[TradeSignal]:
        """ML-based trading strategy."""
        
        if not self.ml_predictor or not self.ml_predictor.is_trained:
            return None
        
        try:
            prediction = self.ml_predictor.predict(df)
            
            if prediction['confidence'] < TradingConfig.ML_CONFIDENCE_THRESHOLD:
                return None
            
            current_price = df['close'].iloc[-1]
            
            if prediction['signal'] == 'BUY':
                action = SignalAction.BUY
            elif prediction['signal'] == 'SELL':
                action = SignalAction.SELL
            else:
                return None
            
            # Calculate stop loss and take profit
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else current_price * 0.02
            if pd.isna(atr):
                atr = current_price * 0.02
            
            if action == SignalAction.BUY:
                stop_loss = current_price - (2 * atr)
                take_profit = current_price + (3 * atr)
            else:
                stop_loss = current_price + (2 * atr)
                take_profit = current_price - (3 * atr)
            
            return TradeSignal(
                symbol=symbol,
                action=action,
                confidence=prediction['confidence'],
                strategy="ML Prediction",
                price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                ml_prediction=prediction['direction'],
                reasoning=f"ML: {prediction['direction']:.1%} up prob, {prediction['expected_return']:.2f}% expected"
            )
            
        except Exception as e:
            self.logger.error(f"Error in ML strategy: {e}")
            return None
    
    def trend_following_strategy(self, df: pd.DataFrame, symbol: str) -> Optional[TradeSignal]:
        """Trend following using moving averages and ADX."""
        
        if df is None or len(df) < 50:
            return None
        
        try:
            current_price = df['close'].iloc[-1]
            
            # Get indicators
            sma_20 = df['sma_20'].iloc[-1] if 'sma_20' in df.columns else None
            sma_50 = df['sma_50'].iloc[-1] if 'sma_50' in df.columns else None
            adx = df['adx'].iloc[-1] if 'adx' in df.columns else None
            
            if any(pd.isna([sma_20, sma_50])):
                return None
            
            # Check for strong trend (ADX > 25)
            adx_value = adx if not pd.isna(adx) else 20
            
            if adx_value < 20:
                return None  # No strong trend
            
            # Determine trend direction
            if current_price > sma_20 > sma_50:
                action = SignalAction.BUY
                confidence = min(0.85, 0.5 + (adx_value / 100))
                reasoning = f"Uptrend: Price > SMA20 > SMA50, ADX: {adx_value:.1f}"
            elif current_price < sma_20 < sma_50:
                action = SignalAction.SELL
                confidence = min(0.85, 0.5 + (adx_value / 100))
                reasoning = f"Downtrend: Price < SMA20 < SMA50, ADX: {adx_value:.1f}"
            else:
                return None
            
            # Calculate stop loss and take profit
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else current_price * 0.02
            if pd.isna(atr):
                atr = current_price * 0.02
            
            if action == SignalAction.BUY:
                stop_loss = sma_20 - atr
                take_profit = current_price + (4 * atr)
            else:
                stop_loss = sma_20 + atr
                take_profit = current_price - (4 * atr)
            
            return TradeSignal(
                symbol=symbol,
                action=action,
                confidence=confidence,
                strategy="Trend Following",
                price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                reasoning=reasoning
            )
            
        except Exception as e:
            self.logger.error(f"Error in trend following strategy: {e}")
            return None
    
    def get_combined_signal(self, signals: List[TradeSignal]) -> Optional[TradeSignal]:
        """Combine multiple signals into one consensus signal."""
        
        if not signals:
            return None
        
        if len(signals) == 1:
            return signals[0]
        
        # Count buy and sell votes weighted by confidence
        buy_weight = 0
        sell_weight = 0
        
        for signal in signals:
            if signal.action in [SignalAction.BUY, SignalAction.STRONG_BUY]:
                weight = signal.confidence
                if signal.action == SignalAction.STRONG_BUY:
                    weight *= 1.5
                buy_weight += weight
            elif signal.action in [SignalAction.SELL, SignalAction.STRONG_SELL]:
                weight = signal.confidence
                if signal.action == SignalAction.STRONG_SELL:
                    weight *= 1.5
                sell_weight += weight
        
        total_weight = buy_weight + sell_weight
        if total_weight == 0:
            return None
        
        # Determine consensus
        if buy_weight > sell_weight * 1.5:
            action = SignalAction.BUY
            confidence = buy_weight / total_weight
        elif sell_weight > buy_weight * 1.5:
            action = SignalAction.SELL
            confidence = sell_weight / total_weight
        else:
            return None  # No consensus
        
        # Use the best signal's price levels
        best_signal = max(signals, key=lambda s: s.confidence)
        
        return TradeSignal(
            symbol=best_signal.symbol,
            action=action,
            confidence=confidence,
            strategy="Combined Signal",
            price=best_signal.price,
            stop_loss=best_signal.stop_loss,
            take_profit=best_signal.take_profit,
            reasoning=f"Consensus from {len(signals)} strategies"
        )

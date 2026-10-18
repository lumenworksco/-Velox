"""Technical indicators for Version 6 Trading App."""

import pandas as pd
import numpy as np
from typing import Optional
from .config import TALIB_AVAILABLE, TradingConfig

if TALIB_AVAILABLE:
    import talib


class AdvancedIndicators:
    """Calculate advanced technical indicators."""
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators."""
        
        if df is None or len(df) < 50:
            return df
        
        df = df.copy()
        
        # Ensure column names are lowercase
        df.columns = [col.lower() for col in df.columns]
        
        # Simple Moving Averages
        df['sma_10'] = df['close'].rolling(window=10).mean()
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['sma_200'] = df['close'].rolling(window=200).mean()
        
        # Exponential Moving Averages
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # RSI
        df['rsi'] = AdvancedIndicators.calculate_rsi(df['close'])
        
        # Bollinger Bands
        bb_window = TradingConfig.BB_WINDOW
        bb_std = TradingConfig.BB_STD_DEV
        df['bb_middle'] = df['close'].rolling(window=bb_window).mean()
        bb_std_dev = df['close'].rolling(window=bb_window).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std_dev * bb_std)
        df['bb_lower'] = df['bb_middle'] - (bb_std_dev * bb_std)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_percent'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # ATR (Average True Range)
        df['atr'] = AdvancedIndicators.calculate_atr(df)
        
        # Stochastic Oscillator
        stoch = AdvancedIndicators.calculate_stochastic(df)
        df['stoch_k'] = stoch['k']
        df['stoch_d'] = stoch['d']
        
        # Volume indicators
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # OBV (On-Balance Volume)
        df['obv'] = AdvancedIndicators.calculate_obv(df)
        
        # VWAP
        df['vwap'] = AdvancedIndicators.calculate_vwap(df)
        
        # ADX (Average Directional Index)
        df['adx'] = AdvancedIndicators.calculate_adx(df)
        
        # CCI (Commodity Channel Index)
        df['cci'] = AdvancedIndicators.calculate_cci(df)
        
        # Williams %R
        df['williams_r'] = AdvancedIndicators.calculate_williams_r(df)
        
        # Price momentum
        df['momentum'] = df['close'].pct_change(periods=10) * 100
        df['roc'] = ((df['close'] / df['close'].shift(10)) - 1) * 100
        
        # Support/Resistance levels
        df['pivot'] = (df['high'].shift(1) + df['low'].shift(1) + df['close'].shift(1)) / 3
        df['r1'] = 2 * df['pivot'] - df['low'].shift(1)
        df['s1'] = 2 * df['pivot'] - df['high'].shift(1)
        df['r2'] = df['pivot'] + (df['high'].shift(1) - df['low'].shift(1))
        df['s2'] = df['pivot'] - (df['high'].shift(1) - df['low'].shift(1))
        
        # Trend strength
        df['trend_strength'] = abs(df['close'] - df['sma_50']) / df['atr']
        
        return df
    
    @staticmethod
    def calculate_rsi(series: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=window).mean()
        
        return atr
    
    @staticmethod
    def calculate_stochastic(df: pd.DataFrame, k_window: int = 14, 
                            d_window: int = 3) -> dict:
        """Calculate Stochastic Oscillator."""
        
        low_min = df['low'].rolling(window=k_window).min()
        high_max = df['high'].rolling(window=k_window).max()
        
        k = 100 * ((df['close'] - low_min) / (high_max - low_min))
        d = k.rolling(window=d_window).mean()
        
        return {'k': k, 'd': d}
    
    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.Series:
        """Calculate On-Balance Volume."""
        
        obv = [0]
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.append(obv[-1] + df['volume'].iloc[i])
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.append(obv[-1] - df['volume'].iloc[i])
            else:
                obv.append(obv[-1])
        
        return pd.Series(obv, index=df.index)
    
    @staticmethod
    def calculate_vwap(df: pd.DataFrame) -> pd.Series:
        """Calculate Volume Weighted Average Price."""
        
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
        
        return vwap
    
    @staticmethod
    def calculate_adx(df: pd.DataFrame, window: int = 14) -> pd.Series:
        """Calculate Average Directional Index."""
        
        high = df['high']
        low = df['low']
        close = df['close']
        
        plus_dm = high.diff()
        minus_dm = low.diff().abs()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs()
        ], axis=1).max(axis=1)
        
        atr = tr.rolling(window=window).mean()
        plus_di = 100 * (plus_dm.rolling(window=window).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=window).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=window).mean()
        
        return adx
    
    @staticmethod
    def calculate_cci(df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Calculate Commodity Channel Index."""
        
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        sma = typical_price.rolling(window=window).mean()
        mad = typical_price.rolling(window=window).apply(
            lambda x: np.abs(x - x.mean()).mean(), raw=True
        )
        
        cci = (typical_price - sma) / (0.015 * mad)
        
        return cci
    
    @staticmethod
    def calculate_williams_r(df: pd.DataFrame, window: int = 14) -> pd.Series:
        """Calculate Williams %R."""
        
        highest_high = df['high'].rolling(window=window).max()
        lowest_low = df['low'].rolling(window=window).min()
        
        williams_r = -100 * (highest_high - df['close']) / (highest_high - lowest_low)
        
        return williams_r
    
    @staticmethod
    def get_trend_direction(df: pd.DataFrame) -> str:
        """Determine the overall trend direction."""
        
        if df is None or len(df) < 50:
            return "SIDEWAYS"
        
        current_price = df['close'].iloc[-1]
        sma_20 = df['sma_20'].iloc[-1] if 'sma_20' in df.columns else df['close'].rolling(20).mean().iloc[-1]
        sma_50 = df['sma_50'].iloc[-1] if 'sma_50' in df.columns else df['close'].rolling(50).mean().iloc[-1]
        
        # Check for NaN
        if pd.isna(sma_20) or pd.isna(sma_50):
            return "SIDEWAYS"
        
        if current_price > sma_20 > sma_50:
            return "BULLISH"
        elif current_price < sma_20 < sma_50:
            return "BEARISH"
        else:
            return "SIDEWAYS"
    
    @staticmethod
    def get_momentum_score(df: pd.DataFrame) -> float:
        """Calculate a momentum score from -100 to 100."""
        
        if df is None or len(df) < 50:
            return 0.0
        
        score = 0.0
        
        # RSI contribution
        if 'rsi' in df.columns:
            rsi = df['rsi'].iloc[-1]
            if not pd.isna(rsi):
                score += (rsi - 50) * 0.4  # -20 to +20
        
        # MACD contribution
        if 'macd_histogram' in df.columns:
            macd_hist = df['macd_histogram'].iloc[-1]
            if not pd.isna(macd_hist):
                score += np.clip(macd_hist * 10, -30, 30)  # -30 to +30
        
        # Price vs SMA contribution
        if 'sma_50' in df.columns:
            price = df['close'].iloc[-1]
            sma = df['sma_50'].iloc[-1]
            if not pd.isna(sma) and sma > 0:
                pct_diff = ((price / sma) - 1) * 100
                score += np.clip(pct_diff * 5, -30, 30)  # -30 to +30
        
        # Stochastic contribution
        if 'stoch_k' in df.columns:
            stoch = df['stoch_k'].iloc[-1]
            if not pd.isna(stoch):
                score += (stoch - 50) * 0.2  # -10 to +10
        
        return np.clip(score, -100, 100)
    
    @staticmethod
    def get_volatility_level(df: pd.DataFrame) -> str:
        """Determine volatility level."""
        
        if df is None or len(df) < 20:
            return "MEDIUM"
        
        if 'bb_width' in df.columns:
            bb_width = df['bb_width'].iloc[-1]
            avg_bb_width = df['bb_width'].mean()
            
            if pd.isna(bb_width) or pd.isna(avg_bb_width):
                return "MEDIUM"
            
            if bb_width > avg_bb_width * 1.5:
                return "HIGH"
            elif bb_width < avg_bb_width * 0.5:
                return "LOW"
            else:
                return "MEDIUM"
        
        return "MEDIUM"

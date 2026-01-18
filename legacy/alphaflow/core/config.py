"""Configuration and dependency management for AlphaFlow Trading App."""

import warnings
import logging
from datetime import datetime, time
from enum import Enum
import pytz
import os

warnings.filterwarnings('ignore')

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# ============================================================================
# TRADING MODE ENUM
# ============================================================================

class TradingMode(Enum):
    """Trading mode enumeration."""
    LIVE = "live"
    PAPER = "paper"
    BACKTEST = "backtest"
    ANALYSIS = "analysis"

# ============================================================================
# DEPENDENCY CHECKS
# ============================================================================

# Core dependency checks
try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError as e:
    print(f"Warning: yfinance import error: {e}")
    YF_AVAILABLE = False

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False

try:
    from alpaca_trade_api import REST, Stream
    from alpaca_trade_api.common import URL
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False

# Deep Learning dependencies
try:
    import torch
    import torch.nn as nn
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

try:
    from transformers import AutoTokenizer, AutoModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Sentiment analysis dependencies
try:
    import nltk
    from textblob import TextBlob
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False

try:
    import tweepy
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False

try:
    from newsapi import NewsApiClient
    NEWS_API_AVAILABLE = True
except ImportError:
    NEWS_API_AVAILABLE = False

# Streamlit check
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    """Setup logging configuration."""
    os.makedirs('logs', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f'logs/trading_app_v6_{timestamp}.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )


# ============================================================================
# MARKET HOURS UTILITIES
# ============================================================================

def is_market_open():
    """Check if US stock market is currently open"""
    try:
        eastern = pytz.timezone('US/Eastern')
        now = datetime.now(eastern)

        if now.weekday() >= 5:
            return False

        market_open = time(9, 30)
        market_close = time(16, 0)
        current_time = now.time()

        return market_open <= current_time <= market_close
    except Exception:
        return True


def get_time_until_market_open():
    """Get seconds until market opens. Returns 0 if market is open."""
    try:
        eastern = pytz.timezone('US/Eastern')
        now = datetime.now(eastern)

        if is_market_open():
            return 0

        days_ahead = 0
        if now.weekday() == 5:
            days_ahead = 2
        elif now.weekday() == 6:
            days_ahead = 1
        elif now.time() >= time(16, 0):
            days_ahead = 1

        next_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        if days_ahead > 0:
            from datetime import timedelta
            next_open += timedelta(days=days_ahead)

        seconds_until_open = (next_open - now).total_seconds()
        return max(0, seconds_until_open)
    except Exception:
        return 0


def get_market_status_message():
    """Get a formatted message about market status"""
    if is_market_open():
        return "🟢 Market is OPEN"
    else:
        seconds = get_time_until_market_open()
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)

        eastern = pytz.timezone('US/Eastern')
        now = datetime.now(eastern)

        if now.weekday() >= 5:
            return f"🔴 Market CLOSED (Weekend) - Opens in {hours}h {minutes}m"
        elif now.time() < time(9, 30):
            return f"🟡 Pre-market - Opens in {hours}h {minutes}m"
        else:
            return f"🔴 After-hours - Opens in {hours}h {minutes}m"


# ============================================================================
# TRADING CONFIGURATION
# ============================================================================

class TradingConfig:
    """Trading configuration constants."""

    # Risk management
    MAX_POSITION_SIZE = 0.1
    MAX_DAILY_LOSS = 0.02
    MAX_DRAWDOWN = 0.15

    # Technical indicators
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    RSI_WINDOW = 14

    # Moving averages
    SMA_SHORT = 10
    SMA_MEDIUM = 20
    SMA_LONG = 50
    SMA_VERY_LONG = 200

    EMA_FAST = 12
    EMA_SLOW = 26
    EMA_SIGNAL = 9

    # Bollinger Bands
    BB_WINDOW = 20
    BB_STD_DEV = 2

    # ATR
    ATR_WINDOW = 14

    # ML parameters
    ML_MIN_SAMPLES = 100
    ML_CONFIDENCE_THRESHOLD = 0.6

    # Deep Learning parameters
    DL_SEQUENCE_LENGTH = 60
    DL_BATCH_SIZE = 32
    DL_EPOCHS = 50
    DL_LEARNING_RATE = 0.001

    # Multi-timeframe settings
    TIMEFRAMES = ['1m', '5m', '15m', '1h', '1d']
    PRIMARY_TIMEFRAME = '5m'

    # Options trading parameters
    OPTIONS_DELTA_MIN = 0.3
    OPTIONS_DELTA_MAX = 0.7
    OPTIONS_DTE_MIN = 7
    OPTIONS_DTE_MAX = 60

    # Sentiment analysis settings
    SENTIMENT_WEIGHT = 0.2
    NEWS_LOOKBACK_HOURS = 24
    SENTIMENT_THRESHOLD = 0.1

    # Trading
    DEFAULT_CHECK_INTERVAL = 300
    MIN_CONFIDENCE = 0.6
    MAX_EXECUTIONS_PER_ITERATION = 2

    # Portfolio
    DEFAULT_INITIAL_CAPITAL = 100000


# ============================================================================
# WATCHLISTS
# ============================================================================

WATCHLISTS = {
    'tech': ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA'],
    'blue_chips': ['AAPL', 'MSFT', 'JNJ', 'PG', 'KO'],
    'growth': ['TSLA', 'NVDA', 'AMD', 'CRM', 'NFLX'],
    'crypto': ['BTC-USD', 'ETH-USD', 'SOL-USD'],
    'etfs': ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI'],
    'default': ['AAPL', 'MSFT', 'GOOGL']
}

OPTIONS_STRATEGIES = {
    'long_call': {
        'description': 'Bullish strategy - buy call option',
        'legs': ['buy_call']
    },
    'long_put': {
        'description': 'Bearish strategy - buy put option',
        'legs': ['buy_put']
    },
    'bull_call_spread': {
        'description': 'Moderately bullish - buy call, sell higher call',
        'legs': ['buy_call', 'sell_call']
    },
    'bear_put_spread': {
        'description': 'Moderately bearish - buy put, sell lower put',
        'legs': ['buy_put', 'sell_put']
    },
    'iron_condor': {
        'description': 'Neutral strategy - profit from low volatility',
        'legs': ['buy_put', 'sell_put', 'sell_call', 'buy_call']
    }
}


# ============================================================================
# DEPENDENCY UTILITIES
# ============================================================================

def get_dependency_status():
    """Get dictionary of all dependency statuses."""
    return {
        'yfinance': YF_AVAILABLE,
        'scikit-learn': SKLEARN_AVAILABLE,
        'TA-Lib': TALIB_AVAILABLE,
        'SciPy': SCIPY_AVAILABLE,
        'Alpaca API': ALPACA_AVAILABLE,
        'PyTorch': PYTORCH_AVAILABLE,
        'Transformers': TRANSFORMERS_AVAILABLE,
        'Sentiment': SENTIMENT_AVAILABLE,
        'Twitter API': TWITTER_AVAILABLE,
        'News API': NEWS_API_AVAILABLE,
        'Streamlit': STREAMLIT_AVAILABLE,
        'Plotly': PLOTLY_AVAILABLE
    }


def install_dependencies():
    """Helper function to install missing dependencies."""
    import subprocess
    import sys

    packages_to_install = []

    if not YF_AVAILABLE:
        packages_to_install.extend(['yfinance', 'websockets>=11.0'])
    if not SKLEARN_AVAILABLE:
        packages_to_install.append('scikit-learn')
    if not SCIPY_AVAILABLE:
        packages_to_install.append('scipy')
    if not ALPACA_AVAILABLE:
        packages_to_install.append('alpaca-trade-api')
    if not PYTORCH_AVAILABLE:
        packages_to_install.append('torch')
    if not TRANSFORMERS_AVAILABLE:
        packages_to_install.append('transformers')
    if not SENTIMENT_AVAILABLE:
        packages_to_install.extend(['nltk', 'textblob'])
    if not TWITTER_AVAILABLE:
        packages_to_install.append('tweepy')
    if not NEWS_API_AVAILABLE:
        packages_to_install.append('newsapi-python')
    if not STREAMLIT_AVAILABLE:
        packages_to_install.append('streamlit')
    if not PLOTLY_AVAILABLE:
        packages_to_install.append('plotly')

    if packages_to_install:
        print(f"Installing missing packages: {', '.join(packages_to_install)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages_to_install)
            print("✅ Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install some packages.")
            return False
    else:
        print("✅ All dependencies are available!")
        return True


def print_dependency_status():
    """Print the status of all dependencies."""
    deps = get_dependency_status()
    print("\n📦 Dependency Status:")
    for name, available in deps.items():
        status = '✅' if available else '❌'
        print(f"   {status} {name}")

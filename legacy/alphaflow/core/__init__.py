"""Core trading modules for AlphaFlow."""

from core.config import (
    TradingConfig,
    TradingMode,
    WATCHLISTS,
    OPTIONS_STRATEGIES,
    setup_logging,
    is_market_open,
    get_market_status_message,
    get_time_until_market_open,
    get_dependency_status,
    YF_AVAILABLE,
    SKLEARN_AVAILABLE,
    SCIPY_AVAILABLE,
    TALIB_AVAILABLE,
    ALPACA_AVAILABLE,
    PYTORCH_AVAILABLE,
    TRANSFORMERS_AVAILABLE,
    SENTIMENT_AVAILABLE,
    TWITTER_AVAILABLE,
    NEWS_API_AVAILABLE,
    STREAMLIT_AVAILABLE,
    PLOTLY_AVAILABLE,
)

from core.data_structures import (
    SignalAction,
    OptionType,
    OptionAction,
    TradeSignal,
    TradeRecord,
    Position,
    OptionsLeg,
    OptionsSignal,
    OptionsPosition,
    PortfolioSnapshot,
    BacktestResult,
    DeepLearningPrediction,
    ModelEnsemblePrediction,
    MultiTimeframeData,
    SentimentData,
    NewsArticle,
    SocialPost,
    PerformanceMetrics,
)

from core.data_fetcher import SimplifiedDataFetcher, AlpacaDataFetcher
from core.indicators import AdvancedIndicators
from core.strategies import TradingStrategies
from core.risk_manager import RiskManager
from core.portfolio_manager import PortfolioManager
from core.backtester import BacktestEngine
from core.trading_engine import TradingEngine

__all__ = [
    # Config
    'TradingConfig',
    'TradingMode',
    'WATCHLISTS',
    'OPTIONS_STRATEGIES',
    'setup_logging',
    'is_market_open',
    'get_market_status_message',
    'get_time_until_market_open',
    'get_dependency_status',
    # Dependency flags
    'YF_AVAILABLE',
    'SKLEARN_AVAILABLE',
    'SCIPY_AVAILABLE',
    'TALIB_AVAILABLE',
    'ALPACA_AVAILABLE',
    'PYTORCH_AVAILABLE',
    'TRANSFORMERS_AVAILABLE',
    'SENTIMENT_AVAILABLE',
    'TWITTER_AVAILABLE',
    'NEWS_API_AVAILABLE',
    'STREAMLIT_AVAILABLE',
    'PLOTLY_AVAILABLE',
    # Data structures
    'SignalAction',
    'OptionType',
    'OptionAction',
    'TradeSignal',
    'TradeRecord',
    'Position',
    'OptionsLeg',
    'OptionsSignal',
    'OptionsPosition',
    'PortfolioSnapshot',
    'BacktestResult',
    'DeepLearningPrediction',
    'ModelEnsemblePrediction',
    'MultiTimeframeData',
    'SentimentData',
    'NewsArticle',
    'SocialPost',
    'PerformanceMetrics',
    # Core classes
    'SimplifiedDataFetcher',
    'AlpacaDataFetcher',
    'AdvancedIndicators',
    'TradingStrategies',
    'RiskManager',
    'PortfolioManager',
    'BacktestEngine',
    'TradingEngine',
]

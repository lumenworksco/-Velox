"""Data structures for Version 6 Trading App."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum


class SignalAction(Enum):
    """Trading signal actions."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"


class OptionType(Enum):
    """Option types."""
    CALL = "call"
    PUT = "put"


class OptionAction(Enum):
    """Option trade actions."""
    BUY = "buy"
    SELL = "sell"


@dataclass
class TradeSignal:
    """Represents a trading signal."""
    symbol: str
    action: SignalAction
    confidence: float
    strategy: str
    price: float
    timestamp: datetime = field(default_factory=datetime.now)
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    quantity: int = 0
    reasoning: str = ""
    
    # V5+ features
    sentiment_score: float = 0.0
    ml_prediction: float = 0.0
    dl_prediction: float = 0.0
    timeframe_confluence: int = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'symbol': self.symbol,
            'action': self.action.value,
            'confidence': self.confidence,
            'strategy': self.strategy,
            'price': self.price,
            'timestamp': self.timestamp.isoformat(),
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'quantity': self.quantity,
            'reasoning': self.reasoning,
            'sentiment_score': self.sentiment_score,
            'ml_prediction': self.ml_prediction,
            'dl_prediction': self.dl_prediction,
            'timeframe_confluence': self.timeframe_confluence
        }


@dataclass
class TradeRecord:
    """Record of an executed trade."""
    symbol: str
    action: str
    entry_price: float
    quantity: int
    entry_time: datetime
    strategy: str
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    pnl: float = 0.0
    pnl_percent: float = 0.0
    status: str = "OPEN"
    notes: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'symbol': self.symbol,
            'action': self.action,
            'entry_price': self.entry_price,
            'quantity': self.quantity,
            'entry_time': self.entry_time.isoformat(),
            'strategy': self.strategy,
            'exit_price': self.exit_price,
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'pnl': self.pnl,
            'pnl_percent': self.pnl_percent,
            'status': self.status,
            'notes': self.notes
        }


@dataclass
class Position:
    """Represents an open position."""
    symbol: str
    quantity: int
    entry_price: float
    current_price: float
    entry_time: datetime
    strategy: str
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    @property
    def market_value(self) -> float:
        return self.quantity * self.current_price
    
    @property
    def cost_basis(self) -> float:
        return self.quantity * self.entry_price
    
    @property
    def unrealized_pnl(self) -> float:
        return self.market_value - self.cost_basis
    
    @property
    def unrealized_pnl_percent(self) -> float:
        if self.cost_basis == 0:
            return 0.0
        return (self.unrealized_pnl / self.cost_basis) * 100

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'symbol': self.symbol,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'entry_time': self.entry_time.isoformat(),
            'strategy': self.strategy,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'market_value': self.market_value,
            'cost_basis': self.cost_basis,
            'unrealized_pnl': self.unrealized_pnl,
            'unrealized_pnl_percent': self.unrealized_pnl_percent
        }


@dataclass
class OptionsLeg:
    """Single leg of an options strategy."""
    option_type: OptionType
    action: OptionAction
    strike: float
    expiry: datetime
    premium: float
    quantity: int = 1
    delta: float = 0.0
    gamma: float = 0.0
    theta: float = 0.0
    vega: float = 0.0


@dataclass
class OptionsSignal:
    """Signal for options trading."""
    symbol: str
    strategy_name: str
    legs: List[OptionsLeg]
    confidence: float
    max_risk: float
    max_profit: float
    breakeven_points: List[float]
    timestamp: datetime = field(default_factory=datetime.now)
    reasoning: str = ""


@dataclass
class PortfolioSnapshot:
    """Snapshot of portfolio state."""
    timestamp: datetime
    cash: float
    positions_value: float
    total_value: float
    daily_pnl: float
    daily_pnl_percent: float
    total_pnl: float
    total_pnl_percent: float
    positions_count: int


@dataclass
class BacktestResult:
    """Results from a backtest run."""
    symbol: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_value: float
    total_return: float
    total_return_percent: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    profit_factor: float
    trades: List[TradeRecord] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'symbol': self.symbol,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'initial_capital': self.initial_capital,
            'final_value': self.final_value,
            'total_return': self.total_return,
            'total_return_percent': self.total_return_percent,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': self.sharpe_ratio,
            'win_rate': self.win_rate,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'avg_win': self.avg_win,
            'avg_loss': self.avg_loss,
            'profit_factor': self.profit_factor
        }


# ============================================================================
# V5 Advanced Structures - Deep Learning, Multi-Timeframe, Sentiment
# ============================================================================

@dataclass
class DeepLearningPrediction:
    """Output from deep learning models (LSTM, Transformer)."""
    symbol: str
    model_type: str  # 'LSTM', 'Transformer', 'Hybrid'
    prediction: float  # Predicted return
    confidence: float  # Model confidence 0-1
    price_targets: Dict[str, float]  # 'short', 'medium', 'long' term
    volatility_forecast: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ModelEnsemblePrediction:
    """Combined prediction from multiple models."""
    symbol: str
    lstm_prediction: Optional[DeepLearningPrediction]
    transformer_prediction: Optional[DeepLearningPrediction]
    ml_prediction: float  # From traditional ML
    ensemble_prediction: float  # Weighted combination
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MultiTimeframeData:
    """Container for data across multiple timeframes."""
    symbol: str
    timeframes: Dict[str, 'pd.DataFrame']  # timeframe -> data
    timestamp: datetime = field(default_factory=datetime.now)

    def get_timeframe(self, timeframe: str):
        """Get data for specific timeframe."""
        return self.timeframes.get(timeframe)


@dataclass
class SentimentData:
    """Sentiment analysis data."""
    symbol: str
    news_sentiment: float  # -1.0 to 1.0
    social_sentiment: float  # -1.0 to 1.0
    combined_sentiment: float  # -1.0 to 1.0
    news_count: int
    social_mentions: int
    timestamp: datetime = field(default_factory=datetime.now)
    sources: List[str] = field(default_factory=list)


@dataclass
class NewsArticle:
    """Individual news article."""
    title: str
    description: str
    source: str
    url: str
    published_at: datetime
    sentiment: float  # -1.0 to 1.0


@dataclass
class SocialPost:
    """Social media post."""
    text: str
    source: str  # 'twitter', 'reddit', etc.
    author: str
    timestamp: datetime
    engagement: int  # likes, retweets, etc.
    sentiment: float  # -1.0 to 1.0


@dataclass
class OptionsPosition:
    """Represents an open options position."""
    symbol: str
    strategy_name: str
    legs: List[OptionsLeg]
    entry_time: datetime
    current_value: float
    initial_cost: float
    max_risk: float
    max_profit: float

    @property
    def unrealized_pnl(self) -> float:
        """Calculate unrealized P&L."""
        return self.current_value - self.initial_cost

    @property
    def unrealized_pnl_percent(self) -> float:
        """Calculate unrealized P&L as percentage."""
        if self.initial_cost == 0:
            return 0.0
        return (self.current_value - self.initial_cost) / abs(self.initial_cost) * 100


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics."""
    total_trades: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    total_return: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    max_drawdown: float = 0.0
    current_portfolio_value: float = 0.0
    var_95: float = 0.0  # Value at Risk 95%
    beta: float = 0.0
    strategy_performance: Dict = field(default_factory=dict)


# Alias for backwards compatibility with V5
OptionLeg = OptionsLeg

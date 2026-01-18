# 🚀 AlphaFlow Trading Platform

A professional algorithmic trading platform for macOS, featuring a Bloomberg Terminal-inspired interface and comprehensive trading capabilities.

![Version](https://img.shields.io/badge/version-6.2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)
![Progress](https://img.shields.io/badge/progress-95%25-brightgreen.svg)

---

## ✨ Features

### 🎯 Trading Capabilities
- **Live Trading** - Execute trades on Alpaca Markets (live account)
- **Paper Trading** - Risk-free strategy testing (Alpaca paper account)
- **Backtesting** - Historical strategy validation with equity curves and metrics
- **Strategy Management** - Deploy, monitor, and control automated trading strategies
- **Analysis Mode** - Market analysis with 20+ technical indicators
- **Real-Time Streaming** - WebSocket streaming for live quotes and trades
- **Quick Order Entry** - Market and limit orders from Trading page
- **Alert System** - Price alerts, technical indicators, and custom notifications

### 📊 Professional Interface
- **Bloomberg-Style UI** - Dark theme with professional data grids
- **Real-time Data** - Live price streaming via WebSocket
- **Professional Charts** - Candlestick charts with technical indicators
- **Multi-Panel Layout** - 7 professional tabs (Dashboard, Trading, Positions, Orders, Strategies, Backtest, Settings)
- **Keyboard Shortcuts** - Fast navigation (Cmd+1-7 for tabs)
- **Settings Management** - Complete UI for API and risk configuration
- **Visual Strategy Cards** - Monitor automated strategies at a glance
- **Backtest Interface** - Full-featured strategy testing with results visualization

### 🧠 Advanced Analytics
- **Technical Indicators** - RSI, MACD, Bollinger Bands, ADX, Stochastic, and 15+ more
- **Machine Learning** - Gradient Boosting and Random Forest predictions
- **Deep Learning** - LSTM and Transformer models for price forecasting
- **Sentiment Analysis** - News and social media sentiment scoring
- **Multi-Timeframe Analysis** - Analyze trends across 1m, 5m, 15m, 1h, 1d
- **Options Trading** - Black-Scholes pricing with Greeks (Delta, Gamma, Theta, Vega)

### ⚠️ Risk Management
- **Position Sizing** - Automatic calculation based on risk parameters
- **Stop-Loss/Take-Profit** - Automated risk controls
- **Daily Loss Limits** - Prevent catastrophic losses
- **Portfolio VaR** - Value at Risk calculations
- **Correlation Analysis** - Portfolio diversification metrics

---

## 📦 Installation

### Requirements
- **macOS 12+** (Monterey or later)
- **Python 3.10+**
- **Alpaca Markets Account** (for trading)

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/AlphaFlow.git
cd AlphaFlow

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
cp .env.example .env
# Edit .env with your Alpaca API credentials

# 5. Launch AlphaFlow
python3 main.py
```

---

## 🔑 API Configuration

AlphaFlow requires Alpaca Markets API credentials. Sign up for free at [alpaca.markets](https://alpaca.markets).

### Get Your API Keys

1. Create an Alpaca account
2. Generate API keys (both paper and live)
3. Add them to `.env`:

```env
# Alpaca API Credentials
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here

# Optional: News API (for sentiment analysis)
NEWS_API_KEY=your_newsapi_key_here

# Optional: Twitter API (for social sentiment)
TWITTER_API_KEY=your_twitter_key_here
TWITTER_API_SECRET=your_twitter_secret_here
```

### Trading Modes

- **Paper Trading** (Default) - Uses Alpaca paper trading endpoint, no real money
- **Live Trading** - Uses Alpaca live trading endpoint, **real money at risk**
- **Backtest** - Simulated historical trading
- **Analysis** - Read-only market analysis

⚠️ **Always test strategies in paper trading mode first!**

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd+1` - `Cmd+6` | Navigate between tabs |
| `Cmd+N` | New order |
| `Cmd+R` | Refresh data |
| `Cmd+F` | Toggle fullscreen |
| `Cmd+Q` | Quit application |

---

## 🔒 Security & Safety

### Critical Safeguards

1. **Trading Mode Validation**
   - Clear visual indicator (LIVE vs PAPER)
   - Confirmation dialogs for live trades
   - Mode displayed in status bar

2. **API Key Security**
   - Never commit `.env` file
   - Keys loaded from environment variables
   - Sensitive data encrypted in memory

3. **Risk Controls**
   - Position size limits enforced
   - Daily loss limits prevent runaway losses
   - Emergency kill switch halts all trading

### Best Practices

- ✅ Start with paper trading
- ✅ Test strategies thoroughly in backtest mode
- ✅ Set conservative risk limits
- ✅ Monitor positions regularly
- ✅ Keep API keys secure
- ❌ Never share API keys
- ❌ Never run untested strategies with real money
- ❌ Never exceed risk tolerance

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🐛 Troubleshooting

### Common Issues

**App won't launch**
```bash
# Check Python version
python3 --version  # Should be 3.10+

# Verify dependencies
pip install -r requirements.txt

# Check logs
tail -f logs/trading_app_v6_*.log
```

**API connection fails**
- Verify API keys in `.env`
- Check internet connection
- Ensure Alpaca API is accessible
- Verify trading mode (paper vs live endpoint)

---

**Built with ❤️ for algorithmic traders**

*Disclaimer: Trading involves risk. Past performance does not guarantee future results. Use at your own risk.*

# AlphaFlow - Professional Algorithmic Trading Platform

![Version](https://img.shields.io/badge/version-7.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![React](https://img.shields.io/badge/react-18.0+-blue.svg)

**A production-ready algorithmic trading platform with Bloomberg Terminal-inspired UI**

---

## 🚀 Features

### Trading Capabilities
- ✅ Live Trading via Alpaca Markets API
- ✅ Paper Trading (simulated funds)
- ✅ Backtesting with historical data
- ✅ 5 Pre-built strategies (MA, RSI, Momentum, etc.)
- ✅ Real-time market data streaming
- ✅ Order management (market/limit/stop)
- ✅ Portfolio tracking with real-time P&L

### Technical Features
- 🎨 Bloomberg Terminal-style UI
- 📊 Candlestick charts with indicators
- 🔄 WebSocket real-time updates
- 🛡️ Risk management (stop-loss, take-profit)
- 📈 Performance analytics (Sharpe, drawdown)
- 🔐 Secure API key management

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Alpaca Markets account ([sign up free](https://alpaca.markets))

### Installation

**1. Clone and setup backend:**
```bash
git clone <repo-url>
cd "Algorithmic Trading"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Setup frontend:**
```bash
cd frontend
npm install
```

**3. Configure environment (`.env`):**
```bash
ALPACA_API_KEY=your_paper_key
ALPACA_SECRET_KEY=your_paper_secret
ALPACA_PAPER=true
INITIAL_CAPITAL=100000
```

**4. Run:**
```bash
# Terminal 1 - Backend
python backend/main.py

# Terminal 2 - Frontend
cd frontend && npm run dev
```

**5. Access:** http://localhost:5173

---

## 📱 Pages

| Page | Description |
|------|-------------|
| **Dashboard** | Portfolio overview, watchlist, metrics |
| **Trading** | Live charts, order entry, positions |
| **Analytics** | Performance metrics, equity curve |
| **Backtest** | Historical strategy testing |
| **Strategies** | Manage and deploy strategies |
| **Settings** | API keys, risk parameters |

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ALPACA_API_KEY` | Alpaca API key | Required |
| `ALPACA_SECRET_KEY` | Alpaca secret | Required |
| `ALPACA_PAPER` | Paper trading | `true` |
| `INITIAL_CAPITAL` | Starting capital | `100000` |
| `MAX_POSITION_SIZE` | Max position ($) | `10000` |
| `MAX_DAILY_LOSS` | Max daily loss ($) | `5000` |

---

## 📊 API Documentation

Interactive docs: http://localhost:8000/api/docs

Key endpoints:
- `GET /api/health` - System health
- `GET /api/market/quote/{symbol}` - Real-time quote
- `POST /api/trading/orders` - Place order
- `POST /api/strategies/{id}/start` - Start strategy
- `POST /api/backtest/run` - Run backtest

---

## 🧪 Testing

### Paper Trading Test
1. Ensure `ALPACA_PAPER=true`
2. Go to Trading page
3. Place test order for AAPL
4. Verify in Orders section

### Backtest Test
1. Go to Backtest page
2. Select "Technical Momentum"
3. Add AAPL, MSFT symbols
4. Set 3-month date range
5. Click "Run Backtest"

---

## 🚨 Safety

### Built-in Protections
- Position size limits
- Daily loss limits
- Stop-loss/take-profit
- Paper trading mode

### Risk Warnings
- ⚠️ Trading involves risk of loss
- ⚠️ Test thoroughly before live trading
- ⚠️ Start with small capital
- ⚠️ This is NOT financial advice

---

## 📚 Documentation

### Getting Started
- [Quick Start Guide](QUICK_START.md) - Get running in 5 minutes
- [Production Deployment](PRODUCTION_DEPLOYMENT.md) - Deploy to production
- [Production Status](PRODUCTION_STATUS.md) - Feature completeness

### Design System
- [Design System](DESIGN_SYSTEM.md) - Complete design specifications
- [Visual Style Guide](VISUAL_STYLE_GUIDE.md) - Visual reference
- [Implementation Guide](DESIGN_IMPLEMENTATION_GUIDE.md) - Code examples
- [Quick Reference](DESIGN_QUICK_REFERENCE.md) - Developer cheat sheet

### API & External
- [API Docs](http://localhost:8000/api/docs) - Interactive API documentation
- [Alpaca Docs](https://alpaca.markets/docs) - Trading API reference

---

## 🏗️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI, Python 3.10+ |
| Frontend | React 18, TypeScript |
| State | TanStack Query |
| Charts | Lightweight Charts |
| Data | yfinance, Alpaca API |
| Indicators | pandas-ta |

---

## ⚠️ Disclaimer

**FOR EDUCATIONAL PURPOSES ONLY**

- Not financial advice
- No warranty provided
- Trading involves risk
- You are responsible for your decisions
- Test in paper trading first

---

## 📞 Support

- Issues: GitHub Issues
- Alpaca: https://alpaca.markets/support

---

**Made for algorithmic traders**  
⭐ Star if helpful!

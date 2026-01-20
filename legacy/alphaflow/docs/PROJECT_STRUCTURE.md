# AlphaFlow - Project Structure Documentation

**Version**: 7.0.0 - Production Release
**Last Updated**: January 20, 2026
**Status**: ✅ PRODUCTION READY

---

## 📁 Root Directory

```
AlphaFlow/
├── backend/                 # FastAPI backend server (8 core modules + 9 API endpoints)
├── frontend/                # React + TypeScript UI (6 pages, 4 components)
├── core/                    # Core trading engine (9 essential modules ONLY)
├── trade_history.json in root (runtime)                    # Application logs (gitignored, only .gitkeep tracked)
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies (29 packages)
└── [Documentation Files]    # 11 essential markdown files

Total: 18 directories, 49 files (CLEANED - removed 20+ unused files)
```

---

## 🔧 Backend (`/backend`)

**Purpose**: FastAPI web server providing REST API for trading operations, strategy management, risk control, and system monitoring.

### API Modules (`/backend/api/`)

| File | Purpose |
|------|---------|
| `market_data.py` | Market data endpoints (quotes, history, bars) |
| `portfolio.py` | Portfolio tracking (summary, P&L, history) |
| `trading.py` | Order placement and position management |
| `strategies.py` | Strategy management + emergency stop |
| `positions.py` | Position tracking and P&L monitoring |
| `risk.py` | Risk management (daily stats, halt/resume) |
| `trades.py` | Trade history and performance analytics |
| `system.py` | System health monitoring and diagnostics |
| `settings.py` | Configuration + trading mode toggle (paper/live) |

### Core Backend Modules (`/backend/`)

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application entry point |
| `strategy_executor.py` | Main strategy execution engine |
| `strategy_logic.py` | Signal generation for all 7 strategies |
| `position_manager.py` | Position tracking with real-time P&L |
| `daily_risk_manager.py` | Daily loss limit enforcement (max 2%) |
| `trade_history.py` | **Trade database** (JSON persistence + analytics) |
| `notification_system.py` | **Email/Slack/console alerts** |
| `portfolio_risk.py` | **Portfolio heat + correlation limits** |

**Key Features**:
- 7 trading strategies (MA Crossover, RSI, Momentum, Mean Reversion, Multi-Timeframe, Volatility Breakout, Quick Test)
- Automated trade execution via Alpaca API
- Stop-loss automation (2x ATR)
- Position sizing (1% of portfolio per trade)
- Multi-layer risk protection (position, portfolio, daily)
- Complete trade audit trail
- Emergency kill switch

---

## 🎨 Frontend (`/frontend`)

**Purpose**: React + TypeScript Bloomberg-inspired trading interface.

### Pages (`/frontend/src/pages/`)

| File | Purpose |
|------|---------|
| `Dashboard.tsx` | Portfolio overview, market watchlist, performance charts |
| `Trading.tsx` | Live trading interface with order entry |
| `Strategies.tsx` | Strategy management (start/stop/configure) |
| `Analytics.tsx` | Technical analysis with 20+ indicators |
| `Backtest.tsx` | Historical strategy validation |
| `Settings.tsx` | API keys, risk parameters, trading mode toggle |

### Components (`/frontend/src/components/`)

| File | Purpose |
|------|---------|
| `Layout.tsx` | **Main layout** with emergency stop button + mode indicator |
| `CandlestickChart.tsx` | TradingView-style candlestick charts |
| `OrderEntry.tsx` | Order placement form (market/limit/stop) |
| `WatchlistTable.tsx` | Real-time watchlist with live quotes |

### API Layer (`/frontend/src/api/`)

| File | Purpose |
|------|---------|
| `market.ts` | Market data API calls |
| `settings.ts` | Settings API calls |

**Key Features**:
- Real-time data updates (5-second polling)
- Bloomberg-inspired dark theme
- Emergency stop button (always visible)
- Trading mode indicator (PAPER = blue, LIVE = red)
- Responsive layout
- TypeScript type safety

---

## ⚙️ Core Trading Engine (`/core`)

**Purpose**: Core algorithmic trading logic (data fetching, indicators, strategies, backtesting).

**CLEANED**: Removed 10 unused modules (deep_learning, ml_predictor, multi_timeframe, options_trading, order_manager, portfolio_manager, sentiment_analysis, alert_system, advanced_strategies, position_sizing)

### Essential Core Modules (9 files ONLY)

| File | Purpose | Status |
|------|---------|--------|
| `trading_engine.py` | Main trading engine (order execution, Alpaca integration) | ✅ Used |
| `data_fetcher.py` | Market data fetching (Alpaca + yfinance) | ✅ Used |
| `indicators.py` | 20+ technical indicators (SMA, EMA, RSI, MACD, Bollinger, ATR) | ✅ Used |
| `strategies.py` | Strategy base classes and implementations | ✅ Used |
| `backtester.py` | Historical strategy validation | ✅ Used |
| `risk_manager.py` | Risk management calculations | ✅ Used |
| `config.py` | Configuration and settings | ✅ Used |
| `data_structures.py` | Data models and structures | ✅ Used |
| `__init__.py` | Package initialization | ✅ Used |

**Key Features**:
- Real-time and historical market data
- Comprehensive technical indicators
- Backtesting engine with performance metrics
- Paper trading support
- Live trading integration

**Note**: All unused/experimental modules removed for production clarity.

---

## 📋 Documentation Files

### Essential Guides

| File | Purpose |
|------|---------|
| `README_PRODUCTION.md` | **Main production guide** - Quick start, features, strategies, API docs |
| `DEPLOYMENT_CHECKLIST.md` | **Step-by-step deployment** - Setup, testing, go-live checklist |
| `LIVE_TRADING_READY.md` | **Live trading features** - Notifications, risk management, monitoring |
| `PRODUCTION_READY_SUMMARY.md` | **Feature summary** - Complete overview of all features |
| `PRODUCTION_TRADING_IMPLEMENTED.md` | **Implementation details** - Technical deep dive |

### Project Documentation

| File | Purpose |
|------|---------|
| `README.md` | Main project README |
| `CHANGELOG.md` | Version history and change log |
| `CONTRIBUTING.md` | Contribution guidelines |
| `PROJECT_STRUCTURE.md` | **This file** - Project organization |

---

## 🗂️ Configuration Files

| File | Purpose |
|------|---------|
| `.env.example` | **Environment variables template** (API keys, risk params, notifications) |
| `.env` | Your actual environment variables (GITIGNORED - never commit!) |
| `.gitignore` | Git ignore rules (logs, .env, cache, build artifacts) |
| `requirements.txt` | Python dependencies for backend |
| `frontend/package.json` | Node.js dependencies for frontend |
| `frontend/vite.config.ts` | Vite build configuration |
| `frontend/tsconfig.json` | TypeScript compiler configuration |

**CRITICAL**: Never commit `.env` file - it contains your API keys!

---

## 📊 Logs Directory (`/logs`)

| File | Purpose |
|------|---------|
| `.gitkeep` | Ensures trade_history.json in root (runtime) directory is tracked by git |
| `trade_history.json` | **Trade database** - Every trade logged with full details |
| `*.log` | Application logs (gitignored, not committed) |

**Trade History**: Contains complete audit trail of all trades with:
- Trade ID, timestamp, strategy
- Symbol, side, shares, price
- P&L (for sells), entry price, hold duration
- Stop-loss/take-profit levels
- Order status, Alpaca ID

---

## 🔐 Environment Variables (`.env`)

**Categories**:

1. **Alpaca API** (Required)
   - `ALPACA_API_KEY` - Your Alpaca API key
   - `ALPACA_SECRET_KEY` - Your Alpaca secret key
   - `ALPACA_PAPER` - Trading mode (true = paper, false = live)

2. **Risk Parameters**
   - `MAX_POSITION_SIZE` - Max position size as % of portfolio (default: 0.10 = 10%)
   - `MAX_DAILY_LOSS` - Max daily loss as % (default: 0.02 = 2%)
   - `MAX_DRAWDOWN` - Max drawdown limit (default: 0.15 = 15%)

3. **Notifications** (Optional)
   - **Email**: `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`, `EMAIL_TO`
   - **Slack**: `SLACK_WEBHOOK_URL`

4. **Logging**
   - `LOG_LEVEL` - Logging level (INFO, DEBUG, WARNING, ERROR)
   - `LOG_TO_FILE` - Enable file logging (true/false)

---

## 🚀 Quick Start Commands

### Backend
```bash
# Navigate to project
cd "/Volumes/File System/Algorithmic Trading"

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env and add your Alpaca API keys

# Start backend
python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

### Access Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

---

## 📦 Dependencies

### Python (Backend)
- **Web Framework**: FastAPI, Uvicorn
- **Trading**: Alpaca API, yfinance
- **Data**: pandas, numpy
- **ML**: scikit-learn
- **Configuration**: python-dotenv, pydantic
- **Database**: SQLAlchemy (optional)
- **Testing**: pytest, httpx
- **Utilities**: psutil, requests, aiohttp

### Node.js (Frontend)
- **Framework**: React 18, TypeScript
- **Build Tool**: Vite
- **UI Library**: React Query (TanStack Query)
- **Styling**: CSS modules
- **Charts**: Lightweight Charts (TradingView)
- **HTTP**: fetch API

---

## 🔄 Git Workflow

### Important Git Rules

**NEVER commit**:
- `.env` file (contains API keys)
- `` files (temporary logs)
- `frontend/node_modules/` (dependencies)
- `frontend/.vite/` (build cache)
- `__pycache__/` (Python cache)

**ALWAYS commit**:
- `.env.example` (template for other developers)
- `trade_history.json in root (runtime).gitkeep` (ensures logs directory exists)
- Source code changes
- Documentation updates

### Recommended Workflow
```bash
# 1. Check git status
git status

# 2. Review changes
git diff

# 3. Add files
git add [specific-files]

# 4. Commit with descriptive message
git commit -m "feat: Add new trading strategy"

# 5. Push to remote
git push origin master
```

---

## 🛡️ Production Safety Features

### Multi-Layer Risk Protection

**Layer 1: Position Level**
- 2x ATR stop-loss per position
- 1% position sizing limit
- Real-time stop monitoring

**Layer 2: Portfolio Level**
- Maximum 25% portfolio heat
- Maximum 15% in correlated assets (>0.7 correlation)
- Pre-trade risk validation

**Layer 3: Daily Level**
- 2% maximum daily loss
- Auto-halt trading when limit reached
- Resume requires manual approval

**Layer 4: Emergency Controls**
- One-click emergency stop button
- Stops all strategies immediately
- Closes all positions via market orders
- Instant notifications

**Layer 5: Monitoring**
- Email alerts for every trade
- Slack notifications for critical events
- Complete trade audit trail
- System health monitoring

---

## 📊 Data Flow

```
User Input (Frontend)
    ↓
FastAPI Backend API
    ↓
Strategy Executor
    ↓
Trading Engine
    ↓
Alpaca API (Order Execution)
    ↓
Position Manager (Track Positions)
    ↓
Trade History (Log Trade)
    ↓
Notification System (Alert User)
```

---

## 🎯 Key Architectural Decisions

1. **FastAPI Backend**: Chosen for async support, automatic API docs, and type safety
2. **React Frontend**: Modern UI with TypeScript for type safety
3. **JSON Trade Database**: Simple file-based persistence (can migrate to SQL later)
4. **Multi-Channel Notifications**: Email + Slack + Console for redundancy
5. **Portfolio Risk Manager**: Advanced correlation and heat tracking
6. **Emergency Stop**: Always-visible kill switch for safety
7. **Trading Mode Indicator**: Visual badge prevents accidental live trading

---

## 🔧 Customization Points

### Adding New Strategy
1. Add strategy logic to `backend/strategy_logic.py`
2. Register in `backend/strategy_executor.py`
3. Add to frontend dropdown in `frontend/src/pages/Strategies.tsx`

### Adding New Risk Parameter
1. Add to `.env.example`
2. Load in `backend/daily_risk_manager.py` or `backend/portfolio_risk.py`
3. Add UI control in `frontend/src/pages/Settings.tsx`

### Adding New Notification Channel
1. Add handler to `backend/notification_system.py`
2. Add configuration to `.env.example`
3. Test with `notification_system.alert_trade_executed()`

---

## 📞 Support & Resources

### API Documentation
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### External Resources
- **Alpaca Dashboard**: https://app.alpaca.markets/dashboard
- **Alpaca API Docs**: https://alpaca.markets/docs/api-documentation/

### System Monitoring
- **Health Check**: http://localhost:8000/api/system/health
- **Diagnostics**: http://localhost:8000/api/system/diagnostics
- **Trade History**: http://localhost:8000/api/trades/history

---

## 🎉 Production Checklist

Before going live:
- [ ] Tested in paper mode for 2+ weeks
- [ ] All strategies profitable in paper mode
- [ ] Notifications working (email/Slack)
- [ ] Emergency stop tested
- [ ] Risk parameters configured for capital size
- [ ] Starting with small capital ($1k-$5k)
- [ ] Only running 1-2 strategies
- [ ] Monitoring plan in place (check 3x daily)

---

**Last Updated**: January 20, 2026
**Version**: 7.0.0 - Production Release
**Status**: ✅ FULLY PRODUCTION READY FOR LIVE AUTOMATED TRADING

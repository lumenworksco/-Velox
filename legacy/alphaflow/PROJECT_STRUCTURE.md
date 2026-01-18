# 📁 AlphaFlow Project Structure

Clean, well-organized FastAPI + React trading platform.

## Directory Layout

```
AlphaFlow/
├── 📄 README.md                    # Main documentation
├── 📄 QUICKSTART.md                # 5-minute setup guide
├── 📄 MIGRATION_GUIDE.md           # PyQt6 → Web migration guide
├── 📄 CHANGELOG.md                 # Version history
├── 📄 CONTRIBUTING.md              # Contribution guidelines
├── 📄 LICENSE                      # MIT License
│
├── 🔧 .env.example                 # Environment template
├── 🔧 requirements-backend.txt     # Python dependencies
├── 🚀 start_backend.sh             # Backend startup script
│
├── 🐍 backend/                     # FastAPI Backend
│   ├── main.py                     # FastAPI app entry point
│   ├── api/                        # REST API endpoints
│   │   ├── trading.py              # Order management
│   │   ├── market_data.py          # Market data & quotes
│   │   ├── backtest.py             # Backtesting
│   │   ├── portfolio.py            # Portfolio metrics
│   │   └── strategies.py           # Strategy management
│   └── core/                       # Backend utilities
│       └── websocket_manager.py    # WebSocket connections
│
├── ⚛️  frontend/                   # React Frontend
│   ├── package.json                # npm dependencies
│   ├── vite.config.ts              # Vite configuration
│   ├── tailwind.config.js          # TailwindCSS config
│   ├── tsconfig.json               # TypeScript config
│   ├── index.html                  # HTML entry point
│   └── src/                        # React source code
│       ├── main.tsx                # React entry point
│       ├── App.tsx                 # Main app component
│       ├── index.css               # Global styles
│       ├── pages/                  # Page components
│       │   ├── Dashboard.tsx       # Portfolio overview ✅
│       │   ├── Trading.tsx         # Trading interface
│       │   ├── Analytics.tsx       # Analytics dashboard
│       │   ├── Backtest.tsx        # Backtest UI
│       │   ├── Strategies.tsx      # Strategy management
│       │   └── Settings.tsx        # Settings panel
│       ├── components/             # Reusable UI components
│       │   ├── Layout.tsx          # App layout with sidebar
│       │   ├── MetricCard.tsx      # Metric display cards
│       │   ├── WatchlistTable.tsx  # Stock watchlist table
│       │   └── EquityChart.tsx     # Equity curve chart
│       └── api/                    # API client
│           ├── client.ts           # Axios instance
│           ├── portfolio.ts        # Portfolio API calls
│           └── market.ts           # Market data API calls
│
├── 🧠 core/                        # Trading Logic (Shared)
│   ├── config.py                   # Configuration management
│   ├── data_structures.py          # Data models
│   ├── data_fetcher.py             # Market data fetching
│   ├── indicators.py               # Technical indicators
│   ├── strategies.py               # Trading strategies
│   ├── trading_engine.py           # Core trading engine
│   ├── backtester.py               # Backtest engine
│   ├── ml_predictor.py             # ML predictions
│   ├── deep_learning.py            # LSTM/Transformer models
│   ├── portfolio_manager.py        # Portfolio tracking
│   ├── risk_manager.py             # Risk management
│   ├── order_manager.py            # Order queue
│   ├── alert_system.py             # Alert management
│   ├── multi_timeframe.py          # Multi-timeframe analysis
│   ├── options_trading.py          # Options (Black-Scholes)
│   └── sentiment_analysis.py       # Sentiment scoring
│
├── 📚 docs/                        # Documentation
│   ├── IMPLEMENTATION_STATUS.md    # Feature status
│   ├── ISSUE_RESOLUTION.md         # Bug fix reports
│   ├── UI_IMPROVEMENTS.md          # UI change log
│   ├── USER_GUIDE.md               # User manual
│   └── ...                         # Other docs
│
├── 🧪 tests/                       # Test suite
│   ├── test_core/                  # Core module tests
│   └── test_app/                   # UI tests
│
├── 📦 archive/                     # Archived code
│   └── pyqt6_version/              # Old PyQt6 app
│       ├── app/                    # PyQt6 UI code
│       ├── requirements-pyqt6.txt  # PyQt6 dependencies
│       └── ...                     # Old files
│
└── 📝 logs/                        # Application logs
    └── .gitkeep                    # Track empty dir
```

## Key Files

### Configuration
- `.env` - API keys and secrets (not in git)
- `.env.example` - Template for .env file
- `requirements-backend.txt` - Python dependencies

### Entry Points
- `backend/main.py` - FastAPI server
- `frontend/src/main.tsx` - React app
- `start_backend.sh` - Quick backend start

### Documentation
- `README.md` - Main docs
- `QUICKSTART.md` - Fast setup
- `MIGRATION_GUIDE.md` - Migration info
- `docs/` - Detailed documentation

## Tech Stack

### Backend
- **FastAPI** - Python web framework
- **Uvicorn** - ASGI server
- **WebSockets** - Real-time data
- **Alpaca API** - Trading
- **yfinance** - Market data

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **React Query** - Data fetching
- **Recharts** - Charts
- **Axios** - HTTP client

### Shared
- **pandas** - Data analysis
- **numpy** - Numerical computing
- **scikit-learn** - Machine learning

## Running the App

### Development
```bash
# Terminal 1: Backend
./start_backend.sh

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Access
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│   React     │ ─HTTP─→ │   FastAPI    │ ─────→ │   Alpaca     │
│  Frontend   │ ←JSON── │   Backend    │ ←────  │     API      │
└─────────────┘         └──────────────┘         └──────────────┘
       │                       │
       │                       │
   WebSocket              ┌────▼─────┐
   Real-time        ┌────→│  Core    │
   Updates          │     │  Trading │
                    │     │  Logic   │
                    │     └──────────┘
                    │          │
                    │     ┌────▼─────┐
                    └─────│ Market   │
                          │  Data    │
                          └──────────┘
```

## Code Organization

### Backend API (`backend/api/`)
Each file is a separate API router:
- `trading.py` - Orders, positions
- `market_data.py` - Quotes, history
- `backtest.py` - Strategy testing
- `portfolio.py` - Portfolio metrics
- `strategies.py` - Strategy management

### Frontend Pages (`frontend/src/pages/`)
Each file is a route/page:
- `Dashboard.tsx` - `/` (home)
- `Trading.tsx` - `/trading`
- `Analytics.tsx` - `/analytics`
- `Backtest.tsx` - `/backtest`
- `Strategies.tsx` - `/strategies`
- `Settings.tsx` - `/settings`

### Core Logic (`core/`)
Shared Python modules used by backend:
- Trading algorithms
- Technical indicators
- Backtesting engine
- ML/AI models
- Risk management

## Notes

- **Old PyQt6 code**: Archived in `archive/pyqt6_version/`
- **Logs**: Cleaned on startup, not committed
- **Dependencies**: Separate for backend/frontend
- **Type safety**: TypeScript frontend, Python type hints backend

---

**Version**: 7.0.0 | **Last Updated**: 2026-01-18

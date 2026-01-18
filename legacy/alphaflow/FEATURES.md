# AlphaFlow v7.0.0 - Complete Feature List

## 🎯 Overview

AlphaFlow is a professional algorithmic trading platform built with **FastAPI + React**, designed with a Bloomberg Terminal-inspired interface. The application provides live trading, paper trading, backtesting, and comprehensive analytics.

---

## 🚀 Core Features

### 1. **Trading Interface**
Professional live trading with real-time market data.

**Features:**
- TradingView-style candlestick charts using lightweight-charts
- Live price quotes with bid/ask spreads
- Real-time order placement (Market & Limit orders)
- Position tracking with live P&L updates
- Order history with status tracking
- Symbol search with autocomplete
- Auto-refresh every 2 seconds

**Tech Stack:**
- `lightweight-charts` for professional charting
- React Query for data fetching
- WebSocket for real-time updates

---

### 2. **Strategy Backtesting**
Test your trading strategies on historical data before deploying them live.

**Features:**
- 5 Built-in Strategies:
  - Technical Momentum (RSI + MACD)
  - Mean Reversion (Buy oversold, sell overbought)
  - Breakout Strategy (Bollinger Band breakouts)
  - ML Momentum (Machine learning predictions)
  - Multi-Timeframe Trend Analysis
- Multi-symbol backtesting
- Configurable date ranges
- Real-time progress tracking
- Beautiful equity curve visualization
- Performance metrics: Sharpe Ratio, Max Drawdown, Win Rate, Profit Factor
- Trade-level statistics

**Visualization:**
- Equity curve with gradient fill
- Performance metric cards
- Detailed trade statistics

---

### 3. **Performance Analytics**
Comprehensive analysis of your trading performance.

**Features:**
- Time range selector (1M, 3M, 6M, 1Y, ALL)
- 6 Key Metrics:
  - Total Return
  - Sharpe Ratio
  - Max Drawdown
  - Win Rate
  - Profit Factor
  - Total Trades

- **Charts:**
  - Equity curve over time
  - Drawdown visualization

- **Risk-Adjusted Returns:**
  - Sortino Ratio
  - Calmar Ratio
  - Recovery Factor
  - Alpha & Beta

- **Trade Statistics:**
  - Average trade return
  - Average win vs. average loss
  - Best & worst trades

- **Risk Metrics:**
  - VaR (95% & 99%)
  - CVaR (Conditional Value at Risk)
  - Volatility
  - Correlation to SPY

- **Trade History Table:**
  - Recent 20 trades with full details
  - Entry/exit prices
  - P&L tracking
  - Duration and strategy attribution

---

### 4. **Strategy Management**
Deploy and manage your algorithmic trading strategies.

**Features:**
- Strategy list with status (Active/Paused/Stopped)
- Start/Pause/Stop controls
- Real-time performance metrics per strategy
- Live trading signals with:
  - Buy/Sell/Hold signals
  - Confidence scores
  - Price at signal
  - Reasoning for each signal
- Auto-refresh every 5 seconds for list
- Auto-refresh every 2 seconds for performance
- Delete strategies with confirmation

**Master-Detail Layout:**
- 1/3 width: Strategy list
- 2/3 width: Selected strategy details

---

### 5. **Settings & Configuration**
Complete control over your trading platform.

**Configuration Sections:**

#### API Configuration
- Trading mode selector (Paper Trading / Live Trading)
- Live trading warning alert
- Alpaca API key input
- Alpaca secret key input (masked)
- Secure storage notification

#### Risk Management
- Max daily loss percentage
- Max position size percentage
- Max open positions
- Default risk per trade

#### Notifications
- Order fill notifications
- Strategy signal alerts
- Risk limit alerts
- Price target alerts

#### Display Preferences
- Theme selector (Dark / Light)
- Chart type (Candlestick / Line)
- Default timeframe (1m to 1W)
- Show/hide volume bars

#### Data Settings
- Data provider (Alpaca / Yahoo Finance)
- Cache enable/disable
- Cache expiration time

**Features:**
- Success toast on save
- Real-time form validation
- Disabled states for dependent fields

---

### 6. **Real-Time Data Streaming**
WebSocket-based live market data.

**Features:**
- Custom `useWebSocket` hook
- Custom `useRealtimeQuotes` hook
- Automatic reconnection (max 5 attempts)
- Price flash animations:
  - Green flash on price increase
  - Red flash on price decrease
- Subscribe/unsubscribe to symbols
- Connection status indicator

**Implementation:**
- WebSocket URL: `ws://localhost:8000/ws/quotes`
- JSON message protocol
- Graceful error handling

---

## 🎨 UI/UX Design

### Bloomberg Terminal Theme
Professional dark theme inspired by Bloomberg Terminal.

**Color Palette:**
- Background: `#0A0E27` (Deep navy)
- Surface: `#131722` (Dark charcoal)
- Elevated: `#1E222D` (Raised elements)
- Border: `#2A2E39` (Subtle borders)
- Accent Blue: `#2962FF` (Primary actions)
- Semantic Positive: `#26A69A` (Green for gains)
- Semantic Negative: `#EF5350` (Red for losses)
- Accent Amber: `#FFA726` (Warnings)

**Typography:**
- Primary font: Inter (clean, modern sans-serif)
- Monospace font: Used for numbers, prices, API keys
- Tabular numbers for aligned data

**Components:**
- Metric cards with icons
- Data grids with hover states
- Color-coded badges (Active/Paused/Stopped)
- Gradient-filled charts
- Smooth transitions and animations

---

## 🛠️ Technology Stack

### Frontend
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite (ultra-fast hot reload)
- **Styling:** TailwindCSS with custom Bloomberg theme
- **State Management:**
  - React Query (server state)
  - Zustand (client state - if needed)
- **Charts:**
  - lightweight-charts (TradingView-style)
  - Recharts (analytics charts)
- **Icons:** Lucide React
- **Date Handling:** date-fns
- **Animations:** Framer Motion
- **HTTP Client:** Axios

### Backend
- **Framework:** FastAPI (Python)
- **Server:** Uvicorn with WebSocket support
- **Data Processing:** pandas, numpy
- **Market Data:** Alpaca API, yfinance
- **Trading:** Alpaca Trade API
- **Machine Learning:** scikit-learn
- **Database:** SQLAlchemy (optional)
- **Authentication:** python-jose (future)

### Development
- **Type Safety:** Full TypeScript coverage
- **Linting:** ESLint with React rules
- **Formatting:** Prettier (frontend), Black (backend)
- **Testing:** pytest (backend), vitest (frontend - future)

---

## 📊 Key Metrics

**Pages Built:** 5 major pages
1. Dashboard (Portfolio overview)
2. Trading (Live trading interface)
3. Backtest (Strategy testing)
4. Analytics (Performance analysis)
5. Strategies (Algorithm management)
6. Settings (Configuration)

**Components Built:** 15+ reusable components
- MetricCard
- CandlestickChart
- OrderEntry
- WatchlistTable
- EquityChart
- And more...

**API Endpoints:** 50+ endpoints across:
- /api/trading
- /api/market
- /api/backtest
- /api/analytics
- /api/strategies
- /api/portfolio
- /ws (WebSocket)

**Lines of Code:**
- Frontend: ~5,000+ lines
- Backend: ~3,000+ lines
- Core trading logic: ~2,000+ lines (preserved from v6)

---

## 🔒 Security Features

- API keys stored securely
- Password-masked secret key input
- Trading mode confirmation for live trading
- Risk limits to prevent excessive losses
- Position size limits
- Daily loss circuit breakers

---

## 🚦 Getting Started

### Prerequisites
```bash
Python 3.10+ (3.14 supported)
Node.js 18+
```

### Installation

**1. Clone the repository:**
```bash
git clone <repository-url>
cd AlphaFlow
```

**2. Install backend dependencies:**
```bash
pip install -r requirements-backend.txt
```

**3. Install frontend dependencies:**
```bash
cd frontend
npm install
```

**4. Configure API keys:**
```bash
cp .env.example .env
# Edit .env and add your Alpaca API keys
```

**5. Run the backend:**
```bash
uvicorn backend.main:app --reload
```

**6. Run the frontend:**
```bash
cd frontend
npm run dev
```

**7. Open your browser:**
```
http://localhost:5173
```

---

## 📈 Future Enhancements

**Planned Features:**
- [ ] Strategy builder UI (drag-and-drop)
- [ ] Advanced charting tools (drawing tools, indicators)
- [ ] Multi-account support
- [ ] Real-time alerts via email/SMS
- [ ] Mobile responsive design
- [ ] Strategy marketplace
- [ ] Automated trade journaling
- [ ] Tax reporting integration
- [ ] Social trading features
- [ ] AI-powered strategy recommendations

---

## 📝 License

MIT License - See LICENSE file for details

---

## 👨‍💻 Credits

Built with assistance from Claude Sonnet 4.5 (Anthropic)

---

## 🙏 Acknowledgments

- **Alpaca Markets** for trading API
- **TradingView** for chart design inspiration
- **Bloomberg Terminal** for UI/UX inspiration
- **Recharts** for beautiful React charts
- **lightweight-charts** for professional candlestick charts

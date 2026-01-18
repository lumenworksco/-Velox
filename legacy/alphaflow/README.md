# 🚀 AlphaFlow v7.0 - Professional Trading Platform

A professional algorithmic trading platform built with **FastAPI** + **React** + **TypeScript**.

## ✨ Features

- **📊 Real-time Market Data** - Live quotes and WebSocket streaming
- **💼 Portfolio Management** - Track positions, P&L, and performance
- **📈 Advanced Charting** - Professional charts with Recharts
- **🤖 Strategy Automation** - Deploy and manage trading algorithms
- **📉 Backtesting** - Test strategies on historical data
- **🎨 Bloomberg-Inspired UI** - Clean, professional dark theme
- **⚡ Fast & Modern** - FastAPI backend, React frontend with Vite

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI (Python 3.10+)
- **Real-time**: WebSocket for live data streaming
- **Trading**: Alpaca API integration
- **Data**: yfinance for market data

### Frontend (React + TypeScript)
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite (ultra-fast)
- **Styling**: TailwindCSS (Bloomberg-inspired theme)
- **Charts**: Recharts for visualizations
- **State**: React Query for server state
- **Routing**: React Router

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Alpaca API keys (paper or live)

### 1. Clone & Setup

```bash
cd "/Volumes/File System/Algorithmic Trading"

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install backend dependencies
pip install -r requirements-backend.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Configure API Keys

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Alpaca API keys
nano .env
```

### 3. Start the Application

**Option A: Run Both (Recommended)**
```bash
# Terminal 1 - Backend
./start_backend.sh

# Terminal 2 - Frontend
cd frontend && npm run dev
```

**Option B: Development Mode**
```bash
# Backend with auto-reload
cd backend && python -m uvicorn main:app --reload

# Frontend with hot reload
cd frontend && npm run dev
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 📁 Project Structure

```
AlphaFlow/
├── backend/                 # FastAPI Backend
│   ├── main.py             # Main FastAPI app
│   ├── api/                # API endpoints
│   │   ├── trading.py      # Order management
│   │   ├── market_data.py  # Market data & quotes
│   │   ├── backtest.py     # Backtesting
│   │   ├── portfolio.py    # Portfolio metrics
│   │   └── strategies.py   # Strategy management
│   └── core/               # Core utilities
│       └── websocket_manager.py
│
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── components/    # Reusable components
│   │   ├── api/          # API client
│   │   └── App.tsx       # Main app
│   ├── package.json
│   └── vite.config.ts
│
├── core/                  # Shared trading logic
│   ├── backtester.py     # Backtest engine
│   ├── indicators.py     # Technical indicators
│   ├── strategies.py     # Trading strategies
│   └── ...
│
├── requirements-backend.txt
├── start_backend.sh
└── README.md
```

## 🎨 UI Preview

### Bloomberg-Inspired Design
- **Dark Theme**: Professional dark color scheme
- **Clean Typography**: SF Pro Display + SF Mono
- **Real-time Updates**: Live data with color flash animations
- **Responsive Tables**: Professional data grids
- **Modern Charts**: Interactive visualizations

### Pages
1. **Dashboard** - Portfolio overview, watchlist, equity curve
2. **Trading** - Order placement and management
3. **Analytics** - Performance metrics and analytics
4. **Backtest** - Strategy backtesting interface
5. **Strategies** - Deploy and manage algorithms
6. **Settings** - Configuration and preferences

## 🔌 API Endpoints

### Trading
- `POST /api/trading/orders` - Place order
- `GET /api/trading/orders` - Get orders
- `DELETE /api/trading/orders/{id}` - Cancel order
- `GET /api/trading/positions` - Get positions

### Market Data
- `GET /api/market/quote/{symbol}` - Get quote
- `GET /api/market/quotes` - Get multiple quotes
- `GET /api/market/history/{symbol}` - Get historical data
- `GET /api/market/search` - Search symbols

### Backtest
- `POST /api/backtest/run` - Start backtest
- `GET /api/backtest/status/{id}` - Get status
- `GET /api/backtest/results/{id}` - Get results

### Portfolio
- `GET /api/portfolio/summary` - Portfolio summary
- `GET /api/portfolio/performance` - Performance metrics
- `GET /api/portfolio/history` - Equity curve

## 🔧 Development

### Backend Development
```bash
# Auto-reload on code changes
python -m uvicorn backend.main:app --reload --port 8000

# Run tests
pytest tests/
```

### Frontend Development
```bash
cd frontend

# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📦 Deployment

### Backend (Production)
```bash
# Using Gunicorn
gunicorn backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Using Docker
docker build -t alphaflow-backend .
docker run -p 8000:8000 alphaflow-backend
```

### Frontend (Production)
```bash
cd frontend
npm run build

# Serve dist/ folder with nginx, Vercel, or Netlify
```

## 🛠️ Tech Stack

### Backend
- FastAPI - Modern, fast web framework
- Uvicorn - ASGI server
- WebSockets - Real-time communication
- Alpaca API - Trading execution
- yfinance - Market data
- pandas - Data manipulation
- scikit-learn - Machine learning

### Frontend
- React 18 - UI framework
- TypeScript - Type safety
- Vite - Build tool
- TailwindCSS - Styling
- React Query - Server state
- React Router - Navigation
- Recharts - Charts
- Lucide React - Icons
- Axios - HTTP client

## 🔐 Security

- API keys stored in `.env` (never committed)
- CORS configured for frontend origin
- Input validation with Pydantic
- Type safety with TypeScript

## 📝 License

MIT License - See LICENSE file

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check API documentation at `/api/docs`

---

**Made with FastAPI + React** | **Version 7.0.0** | **Professional Trading Platform**

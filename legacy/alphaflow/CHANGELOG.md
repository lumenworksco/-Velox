# Changelog

All notable changes to AlphaFlow.

## [6.1.0] - 2026-01-18

### Added - Advanced Charting & Real-Time Streaming
- **Professional ChartPanel Widget**
  - Candlestick charts using PyQt6.QtCharts
  - Volume bars with automatic scaling
  - Technical indicator overlays (SMA 20/50, Bollinger Bands)
  - Timeframe selection (1D, 5D, 1M, 3M, 6M, 1Y, YTD, ALL)
  - Toggle-able indicators with visual feedback

- **Complete Trading Page**
  - Symbol search with auto-completion
  - Real-time price display with change indicators
  - Technical signal badges (RSI, MACD, Moving Averages)
  - Quick order entry panel (Market/Limit orders)
  - Integrated chart panel for visual analysis
  - Buy/Sell buttons with instant execution

- **Full Settings Page**
  - API key configuration UI (Alpaca, News API)
  - Save/load settings to .env file
  - Connection testing functionality
  - Trading mode selection with live warning
  - Risk parameters configuration
  - UI preferences (refresh interval, notifications)
  - WebSocket streaming toggle

- **WebSocket Streaming**
  - Real-time quote updates via Alpaca WebSocket
  - Live trade updates with price and volume
  - Automatic reconnection logic
  - Background thread execution
  - Enable/disable streaming at runtime

### Enhanced
- DataController with WebSocket integration
- Main window with new page integrations
- Real-time data updates across all components
- Signal/slot connections for live updates

### Progress
- Overall completion: 85% (up from 75%)
- All high-priority UI features complete
- Professional charting system operational
- Settings management fully functional

## [6.0.0] - 2026-01-18

### Added - Complete Rebuild
- Native PyQt6 macOS application
- Bloomberg Terminal-inspired UI
- Professional dark theme
- Modular architecture (controllers, widgets, pages)
- OrderManager for complete order lifecycle
- DataController for market data management
- TradingController for order execution
- Real-time watchlist with auto-refresh
- Paper trading mode (default)
- Comprehensive documentation

### Fixed
- ML Predictor train/test split bug
- DataFrame column case mismatch
- PyQt6 import errors
- Multiple critical bugs from previous versions

## [1.0.0] - 2026-01-17

### Added
- Native desktop app using PyWebView
- 14 feature pages:
  - Dashboard with portfolio overview
  - Analysis with 20+ technical indicators
  - Portfolio management
  - Backtesting engine
  - Deep Learning (LSTM/Transformer)
  - Multi-timeframe analysis
  - Sentiment analysis
  - Options pricing (Black-Scholes)
  - Trade Journal with psychology tracking
  - Price/RSI/MACD/Volume alerts
  - Risk Analytics (VaR, scenarios)
  - Strategy Lab (visual builder)
  - Settings & configuration
  - About page
- macOS launcher script
- Windows launcher script

### Technical
- Streamlit web framework
- PyWebView for native windows
- Plotly for interactive charts
- scikit-learn for ML predictions
- PyTorch for deep learning
- yfinance for market data
- Alpaca API for trading

---

## Previous Versions

### Version 5 - Advanced ML & Multi-Asset
- Added deep learning models
- Multi-timeframe analysis
- Options trading module
- Sentiment analysis

### Version 4 - Dependencies
- Modular architecture
- Backtesting engine
- Risk management

### Version 3 - API Integration
- Alpaca trading API
- Real-time data

### Version 2 - API
- Basic API connectivity
- Paper trading

### Version 1 - No API
- Initial prototype
- Technical indicators

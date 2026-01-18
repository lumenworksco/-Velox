# 📖 AlphaFlow User Guide

Complete guide to using the AlphaFlow Trading Platform.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard](#dashboard)
3. [Trading](#trading)
4. [Analytics](#analytics)
5. [Orders](#orders)
6. [Strategies](#strategies)
7. [Backtest](#backtest)
8. [Settings](#settings)
9. [Keyboard Shortcuts](#keyboard-shortcuts)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

```bash
# Clone or download AlphaFlow
cd /path/to/AlphaFlow

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your credentials
```

### First Launch

1. **Run AlphaFlow:**
   ```bash
   python3 run_alphaflow.py
   ```

2. **Configure Settings:**
   - Click **⚙️ Settings** tab
   - Enter your Alpaca API credentials
   - Click **Test Connection** to verify
   - Configure risk parameters
   - Click **Save Settings**

3. **Start Trading:**
   - Return to **📊 Dashboard**
   - View your watchlist
   - Navigate to **💹 Trading** to place orders

---

## Dashboard

The Dashboard provides a high-level overview of your portfolio.

### Features

- **Portfolio Metrics:**
  - Portfolio Value
  - Day P&L
  - Total Return
  - Win Rate

- **Watchlist:**
  - Real-time price updates
  - Change indicators (green/red)
  - Quick access to symbols
  - Auto-refresh every 60 seconds

### How to Use

1. **View Portfolio:**
   - Metrics update automatically
   - Green = positive, Red = negative

2. **Monitor Watchlist:**
   - Default watchlist: Tech stocks (AAPL, MSFT, GOOGL, TSLA, NVDA)
   - Click on symbol to view details
   - Data refreshes automatically

---

## Trading

Professional trading interface with charts and order entry.

### Features

- **Symbol Search:** Enter any stock symbol
- **Live Charts:**
  - Candlestick price chart
  - Volume bars
  - Technical indicators (SMA 20/50, Bollinger Bands)
  - Timeframe selection
- **Technical Signals:**
  - RSI (Overbought/Oversold)
  - MACD (Bullish/Bearish)
  - Moving Averages (Trend)
- **Quick Order Entry:**
  - Market orders
  - Limit orders
  - Instant execution

### How to Trade

1. **Search for Symbol:**
   - Enter symbol (e.g., "AAPL")
   - Click **Search**
   - Chart and price display update

2. **Analyze Chart:**
   - View candlesticks and volume
   - Toggle indicators:
     - Click **SMA 20** for 20-day moving average
     - Click **SMA 50** for 50-day moving average
     - Click **BB** for Bollinger Bands
   - Change timeframe (1D, 5D, 1M, 3M, 6M, 1Y, YTD, ALL)

3. **Check Signals:**
   - View RSI badge for momentum
   - Check MACD for trend
   - Review MA for direction

4. **Place Order:**
   - Select **Market** or **Limit**
   - Enter quantity
   - For Limit orders, set price
   - Click **BUY** or **SELL**
   - Confirm in dialog

---

## Analytics

Comprehensive portfolio analysis and risk metrics.

### Positions Tab

- **Open Positions Table:**
  - Symbol, Quantity, Prices
  - P&L (profit/loss)
  - Portfolio weight

- **Allocation Chart:**
  - Pie chart showing position distribution
  - Visual portfolio breakdown

- **Sector Breakdown:**
  - Industry allocation
  - Diversification analysis

### Risk Metrics Tab

- **Performance Ratios:**
  - Beta (market correlation)
  - Alpha (excess returns)
  - Sharpe Ratio (risk-adjusted return)
  - Sortino Ratio (downside risk)

- **Risk Measures:**
  - Volatility
  - VaR (Value at Risk)
  - Max Drawdown
  - Recovery Days

- **Correlation Matrix:**
  - Position correlations
  - Diversification insights

- **Risk Concentration:**
  - Largest position warnings
  - Sector concentration alerts

### Performance Tab

- **Historical Performance Chart:**
  - Portfolio value over time
  - Benchmark comparison

- **Monthly Returns:**
  - Month-by-month breakdown
  - Alpha vs benchmark
  - Win rate tracking

---

## Orders

View and manage all your orders.

### Features

- **Order History Table:**
  - Time, Symbol, Side (BUY/SELL)
  - Quantity, Price
  - Status (Filled, Pending, Canceled, Rejected)

- **Order Status:**
  - ✓ **Filled:** Order executed successfully
  - ⏳ **Pending:** Order awaiting execution
  - ✗ **Canceled:** Order canceled by user
  - ❌ **Rejected:** Order rejected (insufficient funds, invalid, etc.)

### How to Use

1. View all orders in chronological order
2. Check order status
3. Monitor fill prices
4. Track order success rate

---

## Strategies

Deploy and manage automated trading strategies.

### Features

- **Strategy Cards:**
  - Visual status (Running/Stopped)
  - Performance metrics
  - Start/Stop controls
  - Edit/Delete options

- **Performance Monitoring:**
  - Real-time P&L
  - Trades today
  - Win rate

- **Strategy Logs:**
  - Execution history
  - Trade signals
  - Error messages

### How to Use

1. **Create New Strategy:**
   - Click **+ New Strategy**
   - Select strategy type
   - Configure parameters
   - Set symbols
   - Define risk limits

2. **Start Strategy:**
   - Click **Start** on strategy card
   - Strategy begins automated trading
   - Monitor in real-time

3. **Stop Strategy:**
   - Click **Stop** on strategy card
   - All pending orders canceled
   - Positions remain open

4. **Monitor Performance:**
   - View P&L on card
   - Check recent trades
   - Review logs for signals

---

## Backtest

Test trading strategies on historical data.

### Features

- **Strategy Configuration:**
  - Strategy type selection
  - Parameter inputs
  - Symbol selection
  - Date range picker

- **Execution:**
  - Background processing
  - Progress bar
  - Status updates

- **Results:**
  - Performance metrics (Return, Sharpe, Drawdown, Win Rate)
  - Equity curve chart
  - Trade history table
  - P&L breakdown

### How to Backtest

1. **Configure Strategy:**
   - Select strategy type (MA Crossover, RSI, MACD, etc.)
   - Set parameters (if applicable)

2. **Set Date Range:**
   - Choose start date
   - Choose end date
   - Recommended: 1 year minimum

3. **Select Symbols:**
   - Enter symbols (one per line)
   - Example: AAPL, MSFT, GOOGL

4. **Set Parameters:**
   - Initial capital (e.g., $100,000)
   - Commission (e.g., 0.001 = 0.1%)

5. **Run Backtest:**
   - Click **Run Backtest**
   - Wait for completion
   - Review results

6. **Analyze Results:**
   - Check Total Return
   - Review Sharpe Ratio (>1 is good, >2 is excellent)
   - Examine Max Drawdown (lower is better)
   - Study Win Rate
   - Review trade-by-trade history

---

## Settings

Configure AlphaFlow for your needs.

### API Configuration

- **Alpaca API Key:** Your Alpaca API key
- **Alpaca Secret Key:** Your Alpaca secret key
- **News API Key:** (Optional) For news integration
- **Test Connection:** Verify credentials work

### Trading Configuration

- **Trading Mode:**
  - **PAPER:** Safe testing (recommended)
  - **LIVE:** Real money trading ⚠️
  - **BACKTEST:** Historical testing only
  - **ANALYSIS:** Market analysis only

- **Real-Time Streaming:**
  - Enable for WebSocket streaming
  - Faster updates, more data usage
  - Requires valid Alpaca credentials

### Risk Parameters

- **Max Position Size:** Maximum % of portfolio per position
- **Max Daily Loss:** Stop trading if daily loss exceeds %
- **Default Stop Loss:** Automatic stop loss %
- **Default Take Profit:** Automatic profit target %

### UI Preferences

- **Data Refresh Interval:** How often to update data (seconds)
- **Show Trade Notifications:** Enable popup notifications

### How to Configure

1. Enter API keys
2. Click **Test Connection**
3. Select trading mode (start with PAPER)
4. Configure risk parameters conservatively
5. Set refresh interval (60 seconds recommended)
6. Click **Save Settings**
7. **Important:** Some changes require restart

---

## Keyboard Shortcuts

Navigate AlphaFlow faster with keyboard shortcuts.

### Tab Navigation

- **Cmd+1:** Dashboard
- **Cmd+2:** Trading
- **Cmd+3:** Analytics
- **Cmd+4:** Orders
- **Cmd+5:** Strategies
- **Cmd+6:** Backtest
- **Cmd+7:** Settings

### Actions

- **Cmd+N:** New Order
- **Cmd+R:** Refresh Data
- **Cmd+F:** Full Screen
- **Cmd+Q:** Quit AlphaFlow

---

## Best Practices

### For New Users

1. **Start with Paper Trading:**
   - Never start with live money
   - Test thoroughly in paper mode
   - Understand all features first

2. **Set Conservative Risk Limits:**
   - Max position size: 10% or less
   - Max daily loss: 2% or less
   - Always use stop losses

3. **Start Small:**
   - Trade small quantities initially
   - Increase size as you gain confidence
   - Never risk more than you can afford to lose

### Trading

1. **Always Check Charts:**
   - View technical indicators
   - Confirm signals
   - Check multiple timeframes

2. **Use Stop Losses:**
   - Protect your capital
   - Set realistic stops
   - Don't move stops against you

3. **Diversify:**
   - Don't put all capital in one position
   - Spread across sectors
   - Monitor correlation

### Strategy Deployment

1. **Backtest First:**
   - Always backtest before deploying live
   - Test on multiple symbols
   - Test in different market conditions

2. **Start Small:**
   - Deploy with minimal capital first
   - Monitor closely
   - Scale up gradually

3. **Monitor Regularly:**
   - Check strategy performance daily
   - Review logs for errors
   - Stop if performance degrades

### Risk Management

1. **Never Risk More Than 2% Per Trade:**
   - Calculate position size based on stop loss
   - Account for slippage and commission

2. **Diversify:**
   - Multiple symbols
   - Multiple strategies
   - Multiple timeframes

3. **Set Hard Limits:**
   - Daily loss limits
   - Position size limits
   - Don't override in Settings

---

## Troubleshooting

### Connection Issues

**Problem:** "Could not fetch data" error

**Solutions:**
1. Check internet connection
2. Verify API credentials in Settings
3. Click "Test Connection" in Settings
4. Ensure Alpaca account is active
5. Check if market is open

### Data Not Updating

**Problem:** Prices not refreshing

**Solutions:**
1. Check if auto-refresh is enabled
2. Manually refresh with Cmd+R
3. Increase refresh interval in Settings
4. Enable WebSocket streaming for real-time updates

### Orders Not Executing

**Problem:** Orders fail or get rejected

**Solutions:**
1. **Insufficient Funds:** Check account balance
2. **Market Closed:** Wait for market hours
3. **Invalid Symbol:** Verify symbol is correct
4. **Position Limit:** Check max position size setting
5. **Daily Loss Limit:** Check if limit was hit

### Charts Not Loading

**Problem:** Charts don't appear

**Solutions:**
1. Ensure PyQt6.QtCharts is installed: `pip install PyQt6-Charts`
2. Restart AlphaFlow
3. Check console for errors
4. Verify data is available for symbol

### Strategy Not Starting

**Problem:** Strategy card shows "Stopped"

**Solutions:**
1. Click "Start" button on strategy card
2. Check strategy has valid configuration
3. Verify symbols are correct
4. Check logs for error messages
5. Ensure trading mode allows live trading

### Performance Issues

**Problem:** AlphaFlow running slowly

**Solutions:**
1. Increase refresh interval (Settings)
2. Disable WebSocket streaming if not needed
3. Reduce number of watchlist symbols
4. Close other applications
5. Restart AlphaFlow

---

## Getting Help

- **Documentation:** README.md, IMPLEMENTATION_STATUS.md
- **Quick Start:** QUICKSTART.md
- **Code:** Well-commented for developers
- **Issues:** Check console output for error messages

---

## Safety Reminders

⚠️ **IMPORTANT:**

1. **Paper Trading First:** Always test in paper mode
2. **Never Share API Keys:** Keep credentials secure
3. **Start Small:** Begin with minimal capital
4. **Use Stop Losses:** Protect your capital
5. **Understand Risk:** Only trade what you can afford to lose
6. **Market Hours:** Be aware of market open/close times
7. **Regulations:** Follow all applicable trading regulations
8. **Live Mode Warning:** Heed the warning in Settings

---

**Happy Trading! 🚀**

*Remember: AlphaFlow is a tool. Success depends on your strategy, discipline, and risk management.*

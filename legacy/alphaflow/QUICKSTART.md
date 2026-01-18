# ⚡ AlphaFlow - Quick Start Guide

**Version:** 6.3.0 | **Status:** ✅ Ready to Launch

---

## 🚀 Launch in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Launch AlphaFlow
```bash
python3 run_alphaflow.py
```

### Step 3: Start Trading
The app will open automatically. You're ready to go!

---

## 📱 Interface Overview

### 7 Tabs (Use Cmd+1 through Cmd+7)

1. **📊 Dashboard** (Cmd+1)
   - Portfolio overview
   - Real-time watchlist
   - Key metrics at a glance

2. **💹 Trading** (Cmd+2)
   - Search symbols
   - View charts with indicators
   - Place orders (Market/Limit)

3. **📈 Analytics** (Cmd+3)
   - Position breakdown
   - Risk metrics (Sharpe, VaR, etc.)
   - Performance charts

4. **📋 Orders** (Cmd+4)
   - Order history
   - Track status
   - Monitor fills

5. **🤖 Strategies** (Cmd+5)
   - Deploy automated strategies
   - Monitor performance
   - Start/Stop controls

6. **🔬 Backtest** (Cmd+6)
   - Test strategies historically
   - View equity curves
   - Analyze results

7. **⚙️ Settings** (Cmd+7)
   - Configure API keys
   - Set risk limits
   - Trading mode selection

---

## 🎯 First Trade (Paper Mode)

1. Click **💹 Trading** tab (or press Cmd+2)
2. Enter symbol: `AAPL`
3. Click **Search**
4. Review chart and signals
5. Enter quantity: `1`
6. Click **BUY**
7. Confirm order
8. Check **📋 Orders** tab to see fill

**Safe!** Default mode is PAPER (no real money)

---

## ⌨️ Essential Shortcuts

| Shortcut | Action |
|----------|--------|
| Cmd+1    | Dashboard |
| Cmd+2    | Trading |
| Cmd+3    | Analytics |
| Cmd+N    | New Order |
| Cmd+R    | Refresh Data |
| Cmd+Q    | Quit |

---

## 🔧 Optional: Add API Keys

For live trading with Alpaca:

1. Copy template: `cp .env.example .env`
2. Edit `.env`:
   ```
   ALPACA_API_KEY=your_key_here
   ALPACA_SECRET_KEY=your_secret_here
   ```
3. Go to **⚙️ Settings** tab
4. Enter keys
5. Click **Test Connection**
6. Click **Save Settings**

---

## 🧪 Try a Backtest

1. Go to **🔬 Backtest** tab (Cmd+6)
2. Select strategy: **MA Crossover**
3. Choose date range: Last 3 months
4. Enter symbol: `AAPL`
5. Click **Run Backtest**
6. Review equity curve and metrics

---

## 📊 Features Highlights

### Real-Time Data
- Live price updates
- Auto-refresh every 60 seconds
- WebSocket streaming (enable in Settings)

### Professional Charts
- Candlestick + Volume
- SMA 20/50, Bollinger Bands
- Multiple timeframes (1D to ALL)

### Risk Analytics
- Sharpe Ratio, Sortino Ratio
- Value at Risk (VaR)
- Correlation matrix
- Position sizing limits

### Automated Trading
- Deploy strategies with 1 click
- Monitor in real-time
- Backtest before deploying
- Full control (Start/Stop)

---

## ⚠️ Safety First

✅ **Always start in PAPER mode**
- Test strategies thoroughly
- Understand all features
- Set conservative risk limits

✅ **Use risk parameters**
- Max position size: 10% or less
- Daily loss limit: 2% or less
- Always use stop losses

✅ **Never share API keys**
- Keep `.env` file secure
- Don't commit to git
- Rotate keys regularly

---

## 🆘 Troubleshooting

### App Won't Launch?
```bash
# Install missing dependencies
pip install PyQt6 PyQt6-Charts pandas
```

### Charts Not Showing?
```bash
# Install PyQt6-Charts
pip install "PyQt6-Charts>=6.5.0"
```

### Data Not Updating?
- Check internet connection
- Press Cmd+R to refresh
- Enable WebSocket in Settings

### Orders Not Working?
- Verify trading mode (PAPER vs LIVE)
- Check account balance
- Ensure market is open
- Review Settings → Risk Parameters

---

## 📚 More Help

- **Full Guide:** USER_GUIDE.md (562 lines)
- **Launch Help:** LAUNCH_INSTRUCTIONS.md
- **Tech Status:** IMPLEMENTATION_STATUS.md
- **Changes:** CHANGELOG.md

---

## ✨ What You Can Do Right Now

✅ View real-time data for 5 tech stocks
✅ Place paper trades (100% safe)
✅ View professional candlestick charts
✅ Backtest trading strategies
✅ Monitor portfolio analytics
✅ Deploy automated strategies
✅ Track risk metrics (Sharpe, VaR)

---

## 🎉 You're Ready!

AlphaFlow v6.3.0 is **production-ready** with:
- 7 complete pages
- Real-time trading
- Professional charts
- Advanced analytics
- Strategy automation
- Comprehensive backtesting

**Launch now and start exploring!**

```bash
python3 run_alphaflow.py
```

---

**Happy Trading! 📈**

*Remember: Paper trade first, set risk limits, never invest more than you can afford to lose.*

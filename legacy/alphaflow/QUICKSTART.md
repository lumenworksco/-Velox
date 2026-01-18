# ⚡ AlphaFlow Quick Start Guide

Get AlphaFlow running in 5 minutes!

---

## 🚀 Installation

### 1. Prerequisites
- macOS 12+ (Monterey or later)
- Python 3.10 or higher
- Terminal access

### 2. Install Dependencies

```bash
cd "/Volumes/File System/Algorithmic Trading"

# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

**Expected output:** All packages install successfully

---

## 🔑 Configuration (Optional)

AlphaFlow works out-of-the-box with yfinance (no API keys needed), but for full functionality:

### For Paper Trading (Recommended)

1. Sign up for free Alpaca account: https://alpaca.markets
2. Generate paper trading API keys
3. Configure environment:

```bash
cp .env.example .env
nano .env  # or use any text editor
```

4. Add your keys:
```env
ALPACA_API_KEY=your_paper_key_here
ALPACA_SECRET_KEY=your_paper_secret_here
```

**Note:** Start with paper trading! Never use live trading with untested strategies.

---

## 🎮 Launch AlphaFlow

```bash
python3 main.py
```

**What happens:**
1. App window opens (1600x1000 pixels)
2. Bloomberg-style dark theme loads
3. Dashboard shows with 6 tabs
4. Watchlist automatically fetches real data for:
   - AAPL (Apple)
   - MSFT (Microsoft)
   - GOOGL (Google)
   - TSLA (Tesla)
   - NVDA (NVIDIA)
5. Data updates every 60 seconds

---

## 🎯 First Steps

### 1. Explore the Dashboard
- **Portfolio Value** - Shows current total value
- **Day P&L** - Daily profit/loss
- **Watchlist** - Real-time stock prices

### 2. Place Your First Order

**Method 1: Keyboard Shortcut**
- Press `Cmd+N` (or `Ctrl+N` on non-Mac)

**Method 2: Menu**
- File → New Order

**Order Entry:**
1. Enter symbol (e.g., "AAPL")
2. Choose BUY or SELL
3. Select MARKET or LIMIT
4. Enter quantity (shares)
5. Click "Place Order"

**Result:** Order appears in Orders tab, position in Positions tab!

### 3. Navigate with Keyboard

| Shortcut | Action |
|----------|--------|
| `Cmd+1` | Dashboard tab |
| `Cmd+2` | Trading tab |
| `Cmd+3` | Positions tab |
| `Cmd+4` | Orders tab |
| `Cmd+5` | Backtest tab |
| `Cmd+6` | Settings tab |
| `Cmd+N` | New order |
| `Cmd+R` | Refresh data |
| `Cmd+Q` | Quit app |

---

## 📊 Understanding the Interface

### Dashboard Tab
- **Metric Cards** (top) - Portfolio overview
- **Watchlist** (bottom) - Real-time stock prices with:
  - Symbol
  - Current price
  - Price change ($)
  - Change percentage (%)
  - Volume

### Trading Tab
*Coming soon* - Will show charts and order entry

### Positions Tab
Shows your current holdings:
- Symbol
- Quantity (shares)
- Average price paid
- Current price
- P&L (profit/loss)
- P&L % (percentage)

### Orders Tab
Shows order history:
- Time placed
- Symbol
- Side (BUY/SELL)
- Quantity
- Price
- Status (PENDING/FILLED/CANCELED/REJECTED)

---

## 🛡️ Safety Features

### Trading Mode Indicator
Look at the **status bar** (bottom-right):
- **🟡 PAPER** - Safe! Virtual money only
- **🔴 LIVE** - Real money! Be careful!

**Default:** PAPER mode (virtual $100,000)

### Risk Limits (Automatic)
- **Max position size:** 10% of portfolio
- **Max daily loss:** 2% of portfolio
- **Validation:** Orders rejected if limits exceeded

---

## 🐛 Troubleshooting

### App won't launch

**Issue:** `python3: command not found`  
**Fix:** Install Python 3.10+ from python.org

**Issue:** `ModuleNotFoundError: No module named 'PyQt6'`  
**Fix:** Run `pip install -r requirements.txt`

### No data in watchlist

**Issue:** Blank watchlist or errors  
**Check:**
1. Internet connection working?
2. Wait 10 seconds for initial data load
3. Check logs: `tail -f logs/trading_app_v6_*.log`

**Fix:** Press `Cmd+R` to refresh data

### Order fails

**Issue:** "Insufficient cash balance"  
**Reason:** Not enough virtual cash (you start with $100k)
**Fix:** Reduce order quantity or sell some positions

**Issue:** "Order rejected: ..."  
**Reason:** Various (see error message)
**Common:** Invalid symbol, market closed, exceeded position size limit

### Font warning

**Warning:** `Populating font family aliases took X ms...`  
**Impact:** None - just a cosmetic warning
**Reason:** "Inter" font not installed (app uses fallback)
**Fix:** Optional - install Inter font from https://rsms.me/inter/

---

## 💡 Tips & Best Practices

### 1. Start Small
- Begin with small quantities (1-10 shares)
- Test different order types
- Understand the interface before scaling up

### 2. Use Paper Trading
- **Always** test strategies in paper mode first
- Verify everything works as expected
- Only switch to live when confident

### 3. Monitor Positions
- Check Positions tab regularly
- Understand your P&L
- Set mental stop-losses

### 4. Leverage Keyboard Shortcuts
- Much faster than clicking
- Learn `Cmd+1` through `Cmd+6` for tab navigation
- `Cmd+N` for quick order entry

### 5. Refresh Data
- Press `Cmd+R` if data seems stale
- Auto-refresh runs every 60 seconds
- Check status bar for market hours

---

## 📚 Next Steps

### Learn More
- Read full `README.md` for comprehensive features
- Check `IMPLEMENTATION_STATUS.md` for roadmap
- Review `CONTRIBUTING.md` if you want to extend

### Explore Features
- Place different order types (market vs limit)
- Track multiple positions
- Monitor portfolio value changes
- Experiment with different symbols

### Get Advanced (When Ready)
- Configure Alpaca API for paper trading
- Explore backtesting (when implemented)
- Deploy automated strategies (when implemented)

---

## 🆘 Getting Help

**Questions?**
- Check logs: `logs/trading_app_v6_*.log`
- Review `README.md` troubleshooting section
- File GitHub issue (if applicable)

**Feedback?**
- Feature requests welcome
- Bug reports appreciated
- Contributions encouraged (see CONTRIBUTING.md)

---

## 🎉 You're Ready!

You now know how to:
- ✅ Launch AlphaFlow
- ✅ Navigate the interface
- ✅ Place orders
- ✅ Track positions
- ✅ Monitor portfolio

**Happy trading!** 📈

*Remember: This is for educational purposes. Always understand the risks before trading with real money.*

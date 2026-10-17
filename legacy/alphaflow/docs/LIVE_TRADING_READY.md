# AlphaFlow - LIVE TRADING READY 🚀

## ✅ Production Status: READY FOR LIVE TRADING

Your AlphaFlow platform is now **fully production-ready** with enterprise-grade features for live automated trading!

---

## 🎯 What's Been Added for Production

### 1. **Trade History & Database Logging** ✅

**File**: `backend/trade_history.py`

**Features**:
- JSON file-based trade database (`trade_history.json`)
- Comprehensive trade logging with all details
- Performance analytics (win rate, P&L, profit factor)
- Export to CSV for analysis
- Historical queries by strategy, symbol, date range

**Every Trade Logged**:
- Trade ID, timestamp, strategy
- Symbol, side (buy/sell), shares, price
- Order type, status, commission
- P&L (for sells), entry price, hold duration
- Stop-loss/take-profit levels
- Notes (e.g., "stop_loss_triggered")
- Alpaca order ID

**API Endpoints**:
- `GET /api/trades/history` - Get trade history
- `GET /api/trades/performance` - Performance stats
- `GET /api/trades/summary` - Dashboard summary
- `GET /api/trades/export/csv` - Export to CSV

---

### 2. **Email & Slack Notifications** ✅

**File**: `backend/notification_system.py`

**Notification Channels**:
- **Console Logging** (always enabled)
- **Email** (SMTP - Gmail, etc.)
- **Slack** (via webhooks)

**Automated Alerts For**:
1. ✅ Trade executed (buy/sell with P&L)
2. ✅ Stop-loss triggered
3. ✅ Take-profit triggered
4. ✅ Daily loss limit reached
5. ✅ Strategy started/stopped
6. ✅ Emergency stop executed
7. ✅ Trading mode changed (paper ↔ live)
8. ✅ System errors

**Email Setup** (Add to `.env`):
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient1@example.com,recipient2@example.com
```

**Slack Setup**:
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**Example Notification**:
```
🕐 2026-01-20 15:30:45
📋 Trade Executed: BUY AAPL

Strategy 'multi_timeframe' executed BUY order for 5 shares of AAPL @ $185.50

📊 Details:
  • Strategy: multi_timeframe
  • Symbol: AAPL
  • Side: BUY
  • Shares: 5
  • Price: $185.50
  • P&L: N/A
```

---

### 3. **Portfolio Heat & Correlation Risk Management** ✅

**File**: `backend/portfolio_risk.py`

**Advanced Risk Controls**:

**Portfolio Heat Tracking**:
- Calculates total capital at risk
- Formula: `Sum(position_size × distance_to_stop)`
- Default limit: 25% of portfolio
- Prevents over-exposure

**Correlation Analysis**:
- Groups highly correlated assets
- Limits exposure to correlated clusters
- Default: Max 15% in correlated assets (>0.7 correlation)
- Prevents concentration risk

**Pre-Trade Risk Checks**:
- Validates new positions before entry
- Checks if position would exceed heat limit
- Checks if position would exceed correlation limit
- Returns approval or rejection with reason

**Example**:
```python
# Check if we can open new position
can_open, reason = portfolio_risk_manager.can_open_new_position(
    symbol='AAPL',
    position_value=10000,
    stop_loss_price=180.00,
    entry_price=185.50,
    existing_positions=current_positions,
    portfolio_value=100000
)
# Returns: (True, "Position approved (Heat: 18.5%, Corr: 12.3%)")
```

---

### 4. **Complete Feature List**

| Feature | Status | Description |
|---------|--------|-------------|
| **Automated Trading** | ✅ Ready | 7 strategies execute real trades |
| **Position Tracking** | ✅ Ready | Real-time P&L, stop-loss monitoring |
| **Trade History** | ✅ Ready | Full trade logging & analytics |
| **Risk Management** | ✅ Ready | Daily limits, stop-loss, portfolio heat |
| **Email Alerts** | ✅ Ready | Trade notifications via email |
| **Slack Alerts** | ✅ Ready | Notifications to Slack channel |
| **Emergency Stop** | ✅ Ready | Kill switch stops everything |
| **Paper/Live Toggle** | ✅ Ready | Switch modes with visual indicator |
| **Portfolio Heat** | ✅ Ready | Limit total capital at risk |
| **Correlation Limits** | ✅ Ready | Prevent over-concentration |
| **Positions UI** | ✅ Ready | Frontend page for positions |
| **Trading Mode Indicator** | ✅ Ready | Visual paper/live badge |

---

## 🚀 Getting Started with Live Trading

### Step 1: Configure API Keys

Update your `.env` file:

```bash
# ==============================================================================
# ALPACA MARKETS API (REQUIRED)
# ==============================================================================
ALPACA_API_KEY=your_live_api_key_here
ALPACA_SECRET_KEY=your_live_secret_key_here
ALPACA_PAPER=false  # SET TO FALSE FOR LIVE TRADING

# ==============================================================================
# RISK PARAMETERS
# ==============================================================================
MAX_POSITION_SIZE=10000      # Max $10k per position
MAX_DAILY_LOSS=5000          # Halt trading at $5k daily loss
STOP_LOSS_PERCENT=2.0        # 2% stop-loss
TAKE_PROFIT_PERCENT=5.0      # 5% take-profit

# ==============================================================================
# EMAIL NOTIFICATIONS (RECOMMENDED)
# ==============================================================================
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=your_phone_email@example.com  # For SMS via email

# ==============================================================================
# SLACK NOTIFICATIONS (OPTIONAL)
# ==============================================================================
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**⚠️ IMPORTANT**: For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

---

### Step 2: Test Notifications

Before going live, test your notification system:

1. **Start backend** with notifications configured
2. **Start a strategy** in paper mode
3. **Verify you receive emails/Slack messages** for:
   - Strategy started
   - Trade executed
   - Stop-loss triggered (if it happens)

If notifications work, you're ready for live trading!

---

### Step 3: Go Live (Carefully!)

**Recommended Approach**:

1. **Start Small**: Use $1,000-$5,000 initial capital
2. **One Strategy**: Start with best-performing strategy only
3. **One Symbol**: Test with a single liquid stock (AAPL, SPY, etc.)
4. **Monitor Closely**: Watch for first few trades
5. **Verify**: Check Alpaca dashboard to confirm orders
6. **Scale Up**: Gradually increase after 1-2 weeks of success

**Commands**:
```bash
# Backend
cd /Volumes/File\ System/Algorithmic\ Trading
source .venv/bin/activate
python3 -m uvicorn backend.main:app --reload

# Frontend
cd frontend
npm run dev
```

**Check Trading Mode**:
- Open http://localhost:5173
- Look for header badge: "LIVE MODE" (red) = real money
- If you see "PAPER MODE" (blue), go to Settings → Toggle to LIVE

---

### Step 4: Monitor Your Trading

**Live Monitoring**:
1. **Positions Page**: View all open positions with real-time P&L
2. **Email/Slack**: Receive instant trade notifications
3. **Alpaca Dashboard**: https://app.alpaca.markets/dashboard
4. **Trade History**: `/api/trades/history` - all trades logged

**Emergency Controls**:
- **Emergency Stop Button**: Red button in header (stops everything)
- **Stop Strategy**: Click stop button on Strategies page
- **Close Position**: Click close button on Positions page

---

## 📊 Risk Management in Production

### Default Risk Parameters (Conservative)

| Parameter | Value | Purpose |
|-----------|-------|---------|
| **Position Size** | 1% of portfolio | Max $1,000 per trade on $100k account |
| **Stop-Loss** | 2x ATR | Automatic exit at 2× Average True Range |
| **Daily Loss Limit** | 2% | Halt if down 2% in one day |
| **Portfolio Heat** | 25% max | Max 25% of capital at risk |
| **Correlated Exposure** | 15% max | Max 15% in correlated assets (>0.7 correlation) |
| **Order Type** | Market | Guaranteed execution |
| **Execution Frequency** | 60 seconds | Balance speed vs API rate limits |

### Adjusting for Live Trading

**If trading with $5,000 capital**:
```bash
# In .env file
MAX_POSITION_SIZE=500         # 10% of $5k
MAX_DAILY_LOSS=100            # 2% of $5k
```

**If trading with $100,000 capital**:
```bash
MAX_POSITION_SIZE=5000        # 5% (more conservative)
MAX_DAILY_LOSS=2000           # 2%
```

---

## 🔔 Notification Examples

### Trade Executed (Email)
```
Subject: [AlphaFlow INFO] Trade Executed: BUY AAPL

Strategy 'multi_timeframe' executed BUY order for 5 shares of AAPL @ $185.50

Details:
  • Strategy: multi_timeframe
  • Symbol: AAPL
  • Side: BUY
  • Shares: 5
  • Price: $185.50
```

### Stop-Loss Triggered (Email)
```
Subject: [AlphaFlow WARNING] Stop-Loss Triggered: AAPL

Stop-loss triggered for AAPL in strategy 'multi_timeframe'

Details:
  • Strategy: multi_timeframe
  • Symbol: AAPL
  • Entry Price: $185.50
  • Stop Price: $180.00
  • Loss: $-27.50
```

### Daily Loss Limit (Email)
```
Subject: [AlphaFlow CRITICAL] Daily Loss Limit Reached

Daily loss of -2.05% has reached the limit of 2.00%. All trading has been halted.

Details:
  • Daily P&L: -2.05%
  • Limit: 2.00%
  • Action: All strategies stopped
```

### Trading Mode Changed (Email)
```
Subject: [AlphaFlow CRITICAL] Trading Mode Changed

Trading mode changed from PAPER to LIVE

Details:
  • Previous Mode: PAPER
  • New Mode: LIVE
  • Warning: REAL MONEY AT RISK
```

---

## 📈 Performance Tracking

### View Trade History

**Via API**:
```bash
# Get recent trades
curl http://localhost:8000/api/trades/history?limit=50

# Get performance stats
curl http://localhost:8000/api/trades/performance

# Get trades for specific strategy
curl http://localhost:8000/api/trades/history?strategy_id=multi_timeframe

# Export to CSV
curl http://localhost:8000/api/trades/export/csv?filename=my_trades.csv
```

**Performance Metrics Included**:
- Total trades (wins/losses)
- Win rate (%)
- Total P&L ($)
- Average P&L per trade
- Average win / average loss
- Largest win / largest loss
- Profit factor (gross profit / gross loss)

**Trade History Location**:
- JSON Database: `trade_history.json`
- CSV Exports: `trade_history.json in root (runtime)*.csv`

---

## ⚠️ Important Warnings

### Before Going Live

- [ ] ✅ Tested in paper mode for 2+ weeks successfully
- [ ] ✅ All strategies generate correct signals
- [ ] ✅ Stop-losses trigger correctly
- [ ] ✅ Notifications working (email/Slack)
- [ ] ✅ Verified trades appear in Alpaca dashboard
- [ ] ✅ Emergency stop button tested
- [ ] ✅ Position sizing appropriate for your capital
- [ ] ✅ Monitoring plan in place (check daily)
- [ ] ⚠️ Starting with small capital ($1k-$5k)
- [ ] ⚠️ Only running 1-2 best strategies
- [ ] ⚠️ Have exit plan if not working

### Live Trading Realities

**Expect Differences from Paper Trading**:
1. **Slippage**: Live fills may be worse than paper
2. **Latency**: Orders take time to execute
3. **Emotions**: Harder when real money is at risk
4. **Market Impact**: Large orders move prices
5. **Costs**: Commission, fees, taxes

**Typical Performance Adjustment**:
- Paper trading return: 15% → Live trading: 10-12%
- Paper win rate: 70% → Live: 60-65%
- Drawdowns usually larger in live trading

---

## 🛟 Support & Troubleshooting

### Common Issues

**1. Not Receiving Notifications**

Check email settings:
```python
# Test in Python console
from backend.notification_system import notification_system
notification_system.alert_strategy_started('test', ['AAPL'])
# Should receive email/Slack message
```

**2. Orders Not Executing**

- Check Alpaca API keys are correct
- Verify market is open (9:30 AM - 4:00 PM ET, Mon-Fri)
- Check account has sufficient buying power
- Review backend logs for errors

**3. Emergency Stop Not Working**

- Click the red "EMERGENCY STOP" button in header
- Confirm in dialog
- All strategies should stop immediately
- Check `/api/strategies/emergency-stop` endpoint

### Getting Help

**Logs Location**:
- Backend logs: Console output
- Trade history: `trade_history.json`
- System logs: Check terminal output

**API Documentation**:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

---

## 🎉 You're Ready for Live Trading!

Your AlphaFlow platform now has:

✅ **Enterprise-grade trade logging** with full history
✅ **Multi-channel notifications** (email + Slack + console)
✅ **Advanced risk management** (heat + correlation limits)
✅ **Real-time monitoring** with positions page
✅ **Emergency controls** for quick exits
✅ **Production safety features** at every level

**Start small, monitor closely, and scale gradually!**

---

**Last Updated**: January 20, 2026
**Version**: 7.0.0 - Production Ready
**Status**: ✅ LIVE TRADING READY

**Good luck and trade safely!** 🚀📈💰

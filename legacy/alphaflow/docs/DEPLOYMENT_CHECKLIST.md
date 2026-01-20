# AlphaFlow - Production Deployment Checklist

## 🚀 Pre-Deployment Checklist

Use this checklist before deploying to live trading to ensure all systems are ready.

---

## Phase 1: Configuration & Setup

### ✅ Environment Configuration

- [ ] **Copy `.env.example` to `.env`**
  ```bash
  cp .env.example .env
  ```

- [ ] **Configure Alpaca API Keys**
  - [ ] Sign up at https://alpaca.markets
  - [ ] Get paper trading API keys
  - [ ] Add to `.env`: `ALPACA_API_KEY` and `ALPACA_SECRET_KEY`
  - [ ] Set `ALPACA_PAPER=true` for initial testing

- [ ] **Configure Risk Parameters**
  - [ ] `MAX_POSITION_SIZE` - Default: 10000 ($10k per position)
  - [ ] `MAX_DAILY_LOSS` - Default: 5000 ($5k max daily loss)
  - [ ] `STOP_LOSS_PERCENT` - Default: 2.0 (2% stop-loss)
  - [ ] Adjust based on your capital size

- [ ] **Configure Notifications** (Highly Recommended)
  - [ ] **Email Setup**:
    - [ ] Add `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`
    - [ ] Add `EMAIL_FROM` and `EMAIL_TO`
    - [ ] For Gmail: Use [App Password](https://support.google.com/accounts/answer/185833)
  - [ ] **Slack Setup** (Optional):
    - [ ] Create Slack webhook at https://api.slack.com/messaging/webhooks
    - [ ] Add `SLACK_WEBHOOK_URL`

---

## Phase 2: System Testing

### ✅ Backend Testing

- [ ] **Start Backend**
  ```bash
  cd /Volumes/File\ System/Algorithmic\ Trading
  source .venv/bin/activate
  python3 -m uvicorn backend.main:app --reload
  ```

- [ ] **Verify API Health**
  ```bash
  curl http://localhost:8000/api/system/health
  ```
  - [ ] Status should be "healthy" or "degraded" (not "critical")
  - [ ] Alpaca API should show "connected": true
  - [ ] No critical alerts

- [ ] **Test Notification System**
  - [ ] Start a strategy in paper mode
  - [ ] Verify you receive notification email/Slack
  - [ ] Stop strategy and verify notification
  - [ ] Test emergency stop and verify critical alert

- [ ] **Verify All Endpoints**
  - [ ] Open http://localhost:8000/api/docs
  - [ ] Test key endpoints:
    - [ ] `/api/strategies/list`
    - [ ] `/api/positions/list`
    - [ ] `/api/trades/history`
    - [ ] `/api/risk/daily-stats`
    - [ ] `/api/system/health`

### ✅ Frontend Testing

- [ ] **Start Frontend**
  ```bash
  cd frontend
  npm run dev
  ```

- [ ] **Test All Pages**
  - [ ] Dashboard - Portfolio overview loads
  - [ ] Trading - Live quotes working
  - [ ] Strategies - Can start/stop strategies
  - [ ] Positions - Shows open positions
  - [ ] Settings - Can view/update settings

- [ ] **Test Emergency Stop Button**
  - [ ] Visible in header (red button)
  - [ ] Shows confirmation dialog
  - [ ] Executes emergency stop successfully

- [ ] **Test Trading Mode Indicator**
  - [ ] Shows "PAPER MODE" badge (blue) initially
  - [ ] Can switch to "LIVE MODE" in Settings
  - [ ] Badge turns red when in live mode

---

## Phase 3: Paper Trading Validation (2+ Weeks)

### ✅ Strategy Testing

- [ ] **Select 1-2 Strategies to Test**
  - [ ] Recommended: Multi-Timeframe Confluence
  - [ ] Alternative: RSI Mean Reversion
  - [ ] Configure symbols (liquid stocks: AAPL, MSFT, SPY)

- [ ] **Start Strategy in Paper Mode**
  - [ ] Verify `ALPACA_PAPER=true` in `.env`
  - [ ] Start strategy via frontend
  - [ ] Confirm "PAPER MODE" badge visible
  - [ ] Monitor backend logs for activity

- [ ] **Monitor for First Week**
  - [ ] **Daily checks**:
    - [ ] Review email notifications
    - [ ] Check positions page
    - [ ] Verify trades in Alpaca dashboard
    - [ ] Review trade history: `/api/trades/history`
  - [ ] **Weekly review**:
    - [ ] Calculate win rate
    - [ ] Analyze P&L
    - [ ] Review largest win/loss
    - [ ] Check if stop-losses are triggering correctly

### ✅ Validation Criteria

After 2+ weeks of paper trading, verify:

- [ ] **Performance Metrics**
  - [ ] Win rate >= 50%
  - [ ] Positive total P&L
  - [ ] Average win > average loss
  - [ ] Profit factor > 1.0

- [ ] **Risk Management**
  - [ ] Stop-losses triggered correctly
  - [ ] No position exceeded size limit
  - [ ] Daily loss limit never triggered (or triggered correctly)
  - [ ] Portfolio heat stayed below 25%

- [ ] **System Reliability**
  - [ ] No crashes or errors
  - [ ] All notifications received
  - [ ] Trades executed as expected
  - [ ] Emergency stop works when tested

---

## Phase 4: Live Trading Preparation

### ✅ Capital Allocation

- [ ] **Determine Starting Capital**
  - [ ] Recommended: $1,000 - $5,000 for first month
  - [ ] Never risk money you can't afford to lose
  - [ ] Plan for potential 10-20% drawdown

- [ ] **Adjust Risk Parameters**
  - [ ] For $5,000 capital:
    ```bash
    MAX_POSITION_SIZE=500    # 10% of capital
    MAX_DAILY_LOSS=100       # 2% of capital
    ```
  - [ ] For $10,000 capital:
    ```bash
    MAX_POSITION_SIZE=1000   # 10% of capital
    MAX_DAILY_LOSS=200       # 2% of capital
    ```

### ✅ Get Live API Keys

- [ ] **Alpaca Live Account**
  - [ ] Complete Alpaca account verification
  - [ ] Fund account with starting capital
  - [ ] Generate live API keys (NOT paper keys)
  - [ ] Store keys securely

- [ ] **Update .env for Live Trading**
  ```bash
  ALPACA_API_KEY=your_LIVE_key_here
  ALPACA_SECRET_KEY=your_LIVE_secret_here
  ALPACA_PAPER=false  # ⚠️ CRITICAL - SET TO FALSE
  ```

### ✅ Final Safety Checks

- [ ] **Review Trading Plan**
  - [ ] Document which strategies to run
  - [ ] Document which symbols to trade
  - [ ] Define daily monitoring schedule
  - [ ] Set loss limits (when to stop trading)

- [ ] **Backup & Recovery Plan**
  - [ ] Know how to use emergency stop button
  - [ ] Have Alpaca login ready for manual control
  - [ ] Save support contacts
  - [ ] Document recovery procedures

- [ ] **Monitoring Plan**
  - [ ] Schedule: Check 3x per day (morning, midday, close)
  - [ ] Set up phone notifications for critical alerts
  - [ ] Have plan for vacation/illness (stop strategies)

---

## Phase 5: Go Live

### ✅ Day 1: Launch

- [ ] **Morning Pre-Market (Before 9:30 AM ET)**
  - [ ] Restart backend with live credentials
  - [ ] Verify "LIVE MODE" badge shows (RED)
  - [ ] Check system health: `/api/system/health`
  - [ ] Verify notifications working
  - [ ] Review Alpaca account balance

- [ ] **Market Open (9:30 AM ET)**
  - [ ] Start ONLY 1 strategy
  - [ ] Use ONLY 1-2 liquid symbols (AAPL, SPY)
  - [ ] Monitor for first 30 minutes closely
  - [ ] Verify first order appears in Alpaca
  - [ ] Check email notification received

- [ ] **First Trade Review**
  - [ ] Verify order executed at expected price
  - [ ] Check position tracked correctly
  - [ ] Confirm stop-loss set properly
  - [ ] Review notification received

### ✅ Week 1: Close Monitoring

- [ ] **Daily Checks** (3x per day):
  - [ ] Morning: Review overnight activity
  - [ ] Midday: Check open positions and P&L
  - [ ] Close: Review day's trades and performance

- [ ] **Daily Review Checklist**:
  - [ ] How many trades executed?
  - [ ] Win/loss ratio?
  - [ ] Any stop-losses triggered?
  - [ ] Daily P&L percentage?
  - [ ] Any unexpected behavior?
  - [ ] Notifications received for all trades?

- [ ] **End of Week 1**:
  - [ ] Export trade history to CSV
  - [ ] Calculate total P&L
  - [ ] Review largest win/loss
  - [ ] Decide: Continue, adjust, or stop?

---

## Phase 6: Scaling Up (After 1 Month)

### ✅ Performance Review

After 1 month of successful live trading:

- [ ] **Metrics Analysis**
  - [ ] Total return: _______% (Target: > 2%)
  - [ ] Win rate: _______% (Target: > 50%)
  - [ ] Profit factor: _______ (Target: > 1.2)
  - [ ] Max drawdown: _______% (Target: < 10%)
  - [ ] Sharpe ratio: _______ (Target: > 0.5)

- [ ] **System Reliability**
  - [ ] Uptime: _______% (Target: > 99%)
  - [ ] Notification delivery: _______% (Target: 100%)
  - [ ] No critical system errors
  - [ ] All stop-losses functioned correctly

### ✅ Scaling Decision

If performance is good, consider:

- [ ] **Increase Capital**
  - [ ] Add another $5,000
  - [ ] Update `MAX_POSITION_SIZE` and `MAX_DAILY_LOSS`

- [ ] **Add Strategies**
  - [ ] Start a second complementary strategy
  - [ ] Ensure strategies trade different assets (avoid correlation)

- [ ] **Expand Symbols**
  - [ ] Add 2-3 more liquid stocks
  - [ ] Verify they're not highly correlated

---

## Emergency Procedures

### 🚨 If Things Go Wrong

**Immediate Actions**:

1. **Click Emergency Stop Button** (red button in header)
2. **Stop All Strategies** (Strategies page → Stop button)
3. **Review Open Positions** (Positions page → Close manually if needed)
4. **Check Alpaca Dashboard** (verify all closed)
5. **Review Logs** (backend console output)
6. **Switch to Paper Mode** (Settings → Trading Mode → Paper)

**When to Emergency Stop**:
- Daily loss > 2%
- Strategy behaving unexpectedly
- System errors or crashes
- Need to step away from computer
- Market conditions too volatile

---

## Support & Resources

### 📚 Documentation

- **System Health**: http://localhost:8000/api/system/health
- **API Docs**: http://localhost:8000/api/docs
- **Trade History**: http://localhost:8000/api/trades/history
- **Alpaca Dashboard**: https://app.alpaca.markets/dashboard

### 🆘 Getting Help

**Log Locations**:
- Backend logs: Terminal/console output
- Trade history: `logs/trade_history.json`
- System diagnostics: `/api/system/diagnostics`

**Common Issues**:
1. **Orders not executing** → Check market hours, API keys, buying power
2. **No notifications** → Verify SMTP/Slack configuration
3. **High CPU usage** → Reduce number of strategies or symbols
4. **Stop-loss not triggering** → Check position tracking, verify prices

---

## Final Pre-Live Checklist

Before setting `ALPACA_PAPER=false`:

- [ ] ✅ Paper trading successful for 2+ weeks
- [ ] ✅ All strategies tested and profitable
- [ ] ✅ Risk parameters appropriate for capital size
- [ ] ✅ Notifications working (email + Slack)
- [ ] ✅ Emergency stop button tested
- [ ] ✅ Starting capital <= $5,000
- [ ] ✅ Only running 1-2 strategies
- [ ] ✅ Only trading 2-3 liquid symbols
- [ ] ✅ Monitoring plan in place
- [ ] ✅ Emergency procedures understood
- [ ] ✅ Ready to accept losses
- [ ] ✅ Will monitor daily for first month
- [ ] ✅ Have backup plan if not working

---

## ⚠️ CRITICAL REMINDERS

1. **Start Small**: Never risk more than you can afford to lose
2. **Monitor Closely**: Check 3x daily for first month
3. **Trust the System**: Let strategies run, don't override impulsively
4. **Cut Losses**: Use emergency stop if daily loss > 2%
5. **Scale Gradually**: Only increase capital after proven success
6. **Stay Calm**: Losses are part of trading, focus on long-term performance

---

**Last Updated**: January 20, 2026
**Version**: 7.0.0
**Status**: PRODUCTION DEPLOYMENT READY ✅

**Good luck and trade responsibly!** 🚀📈

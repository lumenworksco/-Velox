# Velox (formerly AlphaFlow)

![CI](https://github.com/lumenworksco/Velox/actions/workflows/ci.yml/badge.svg)
![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Interface: terminal](https://img.shields.io/badge/interface-terminal-black.svg)
![Broker: Alpaca](https://img.shields.io/badge/broker-Alpaca-yellow.svg)

**A terminal-native autonomous equity trading system built on the Alpaca API.** Six strategies, an 18-stage signal pipeline with ML confidence gating, a unified exit orchestrator, real-time VaR and a tiered circuit breaker, all driven from one command, `velox`. No browser, no web server: a live Rich dashboard, a status view, a kill switch and a backtester, all in your terminal.

**Philosophy:** Consistent returns over big wins. Target 0.3-0.8% per trade, 65-75% win rate, 15-25 trades/day.

> Velox is the successor to **AlphaFlow**, a Python/FastAPI trading platform, and absorbs ideas from **Trading Algorithms**, a Rust backtesting and paper-trading workspace. See [Lineage](#lineage).

---

## Quick Start

```bash
git clone https://github.com/lumenworksco/Velox.git
cd Velox
pip install -r requirements.txt
cp .env.example .env        # add your Alpaca paper keys
python velox.py run         # live terminal dashboard
```

Or with Docker (`docker compose up -d`, then `docker attach velox-v12` for the dashboard).

### The `velox` command

| Command | What it does |
|---|---|
| `velox run [--live] [--diagnose]` | Run the bot in this terminal with the live dashboard |
| `velox start` / `velox stop` | Run in the background / stop gracefully |
| `velox status [--watch]` | Heartbeat, open positions and recent trades (`--watch` is full-screen) |
| `velox kill` | Emergency kill switch: cancel all orders, close all positions |
| `velox health` | Exit 0 if the heartbeat is fresh (Docker/systemd health check) |
| `velox backtest` | Backtest classic baselines on bundled data, yfinance, or `--strategy velox` for the production engine |
| `velox tearsheet [--days N]` | Performance report from the trade database |
| `velox demo` | Render the dashboard with synthetic data |
| `velox strategies` | Strategies, allocations and baselines |

(`python velox.py ...`, or symlink it onto your `PATH` as `velox`.)

### The terminal dashboard

```bash
python velox.py demo     # preview with synthetic data, no broker needed
```

It shows regime, portfolio and P&L, risk state (vol scalar, beta, P&L lock, consistency), weekly metrics, strategy allocation, open positions, per-strategy breakdown and recent trades.

---

## Strategies

| Strategy | Allocation | Type | Hold | Description |
|---|---|---|---|---|
| **StatMeanReversion** | 28% | Mean Reversion | Intraday | OU process z-score entries with Hurst/ADF filtering on 2-min bars |
| **VWAP v2 Hybrid** | 15% | Mean Reversion | Intraday | VWAP + OU z-score dual confirmation with bid-ask spread filter |
| **KalmanPairsTrader** | 31% | Market-Neutral | Multi-day | Kalman filter dynamic hedge ratios on cointegrated sector pairs |
| **ORB v2** | 0% (disabled) | Breakout | Day | Opening range breakout with gap/range quality filters (10:00-11:30 AM). Demoted 2026-04-17 after an alpha-decay alert; code retained |
| **IntradayMicroMomentum** | 6% | Event-Driven | 8 min | SPY volume spike detection, high-beta stock scalps |
| **PEAD** | 20% | Event-Driven | Multi-day | Post-earnings announcement drift with FinBERT sentiment confirmation |

### How It Works

1. **9:00 AM** -- Dynamic universe selection filters 127+ symbols by volume, market cap, and regime
2. **9:00 AM** -- StatMR builds mean-reversion universe via Hurst exponent, ADF stationarity, and OU half-life
3. **9:00 AM** -- Pre-open gap analysis runs for mean-reversion and breakout strategy calibration
4. **9:30 AM** -- Adaptive scan cycle begins: all strategies scan for signals (interval adjusts based on market activity)
5. **Signal pipeline** -- Each signal passes through 18 stages: data quality gate, MTF confluence, gap analysis, transaction cost filter, VaR check, correlation limiter, sector exposure enforcement, news sentiment, FinBERT scoring, ML confidence gating, signal conflict resolution, and more
6. **ExitOrchestrator** -- Unified exit system with 10-priority-level cascade replaces all legacy exit logic
7. **OMS** -- Orders tracked through 7-state lifecycle (PENDING -> SUBMITTED -> FILLED/CANCELLED/REJECTED)
8. **Every 15 min** -- Beta neutralizer checks portfolio beta and hedges with SPY if |beta| > 0.3
9. **Every 30 min** -- Corporate actions monitoring and position reconciliation with broker
10. **Intraday** -- Correlation matrix refresh keeps sector exposure and effective bets current
11. **Weekly** -- KalmanPairs selects top 15 cointegrated pairs; walk-forward validator checks OOS Sharpe
12. **Friday EOD** -- Tax-loss harvesting evaluates unrealized losses for strategic realization
13. **EOD** -- End-of-day close routine with overnight hold selection

---

## Architecture

```
velox.py                     # The CLI: run / status / kill / backtest / tearsheet ...
main.py                      # Orchestrator: startup, position recovery, main trading loop
dashboard.py                 # Rich live terminal dashboard
config/settings.py           # All strategy and risk parameters
database.py                  # SQLite persistence (trades, positions, snapshots, signal log)
backtester.py                # Production-strategy backtest simulations

engine/                      # Trading engine
  startup.py                 #   module initialisation and startup checks
  scanner.py                 #   strategy scan orchestration with adaptive intervals
  signal_processor.py        #   18-stage signal pipeline with ML gating
  exit_orchestrator.py       #   unified 10-priority exit cascade
  exit_processor.py          #   strategy exits, WebSocket closes
  broker_sync.py             #   position reconciliation with the broker
  daily_tasks.py             #   daily reset, weekly tasks, EOD close, tax harvesting
  profit_maximizer.py        #   adaptive scans, signal stacking, dynamic stops
  events.py, event_log.py    #   pub/sub bus and audit event log

oms/                         # Order management: 7-state orders, idempotency, kill switch
strategies/                  # StatMR, VWAP, KalmanPairs, ORB, MicroMomentum, PEAD, regime, universe
risk/                        # Circuit breaker, VaR, correlation limiter, vol targeting, Kelly,
                             #   P&L lock, beta neutraliser, PDT, portfolio heat, corporate actions
execution/                   # Order routing, TWAP, bracket orders, chase logic, fill analytics
broker/                      # Broker abstraction and paper broker
data/                        # Market data fetching, feed monitor, gap analysis, universe, samples/
ml/                          # Feature pipeline, ensemble inference, training, FinBERT sentiment
analytics/                   # Performance metrics, OU fitting, Hurst, HMM regime, signal ranking
backtesting/                 # Event-driven backtester, attribution, and classic baselines
microstructure/              # VPIN, spread, dark pool, trade classification
compliance/, ops/            # Audit trail, best execution, PDT; disaster recovery, tax harvesting
monitoring/                  # Latency tracker, metrics pipeline, watchdog, reconciliation
scripts/                     # Training, tear sheet, demo dashboard, setup, backup/restore
legacy/                      # Imported AlphaFlow and Trading Algorithms (history preserved)
tests/                       # 1,800+ tests
```

---

## V12 Features

### 18-Stage Signal Pipeline
Every signal passes through a full qualification pipeline including data quality gate, multi-timeframe confluence, gap analysis, transaction cost filter, VaR check, correlation limiter, sector exposure enforcement (30% max), news sentiment, FinBERT scoring, ML confidence gating, signal conflict resolution, and intra-scan entry limits (5 new entries max per scan).

### Unified ExitOrchestrator
A single exit system with 10 priority levels replaces three competing exit subsystems from prior versions. Priority cascade ensures the highest-urgency exit reason always wins (e.g., kill switch overrides trailing stop).

### ML Confidence Gating
4-model averaging ensemble trained with Optuna hyperparameter optimization. 50 core features (reduced from 200+) with 0.947 AUC. FinBERT sentiment runs locally with no paid API dependency. Bayesian Kelly criterion for position sizing.

### Order Management System (OMS)
Full order lifecycle tracking with 7-state machine (PENDING -> SUBMITTED -> PARTIALLY_FILLED -> FILLED / CANCELLED / REJECTED / EXPIRED). Thread-safe registry with idempotency keys prevents duplicate orders. API failure circuit breaker triggers kill switch after 5 failures in 5 minutes. Order rejection classification and chase logic for limit orders.

### Tiered Circuit Breaker
Progressive risk reduction based on daily P&L, plus VIX spike trigger:
- **Yellow** (-1%): Reduce new position sizes by 50%
- **Orange** (-2%): Stop all new entries
- **Red** (-3%): Close day trades, keep swing positions
- **Black** (-4%): Kill switch -- close everything
- **VIX Spike**: Automatic circuit breaker activation on volatility regime change

### VaR Monitor
Real-time portfolio Value-at-Risk using three methods:
- Parametric VaR (95% and 99%)
- Historical simulation
- Monte Carlo (10,000 paths)

### Correlation Limiter with Intraday Refresh
Prevents concentration risk via eigenvalue-based effective bets calculation and sector Herfindahl index monitoring. Correlation matrix refreshes intraday to keep exposure calculations current.

### Position Recovery on Restart
On startup, the bot reconciles with the broker to recover any open positions from a prior session. No positions are orphaned across restarts.

### Corporate Actions Monitoring
Checks for splits, dividends, and other corporate actions every 30 minutes. Adjusts position tracking and alerts on events that could affect open trades.

### Tax-Loss Harvesting
Friday end-of-day routine evaluates unrealized losses for strategic realization, capturing tax benefits while maintaining portfolio exposure.

### Risk Manager Enhancements
Time-of-day risk multiplier (tighter sizing at open/close), Friday risk reduction, and drawdown-based dynamic sizing that scales down as daily losses accumulate.

### Profit Maximizer
Adaptive scan intervals based on market activity, signal stacking for high-conviction entries, momentum persistence detection, dynamic stop adjustment on winning trades, and win-streak-aware sizing.

### Data Feed Monitoring
Alpaca outage detection with automatic fallback to backup protective stops when live data feed goes stale.

### Transaction Cost Filter
Pre-trade expected value check: rejects signals where estimated costs (spread + slippage + commission) exceed expected profit.

### Structured Logging
JSON-formatted logs in production (structlog), human-readable in development.

### Dynamic Universe
Daily symbol selection at 9 AM based on volume, market cap, and current market regime. Adapts universe size and composition to volatility conditions.

---

## Risk Engine

| Component | Description |
|---|---|
| **Tiered Circuit Breaker** | 4-tier progressive risk reduction (-1% to -4%) + VIX spike trigger |
| **VaR Monitor** | Parametric + Historical + Monte Carlo VaR at 95%/99% |
| **Correlation Limiter** | Eigenvalue effective bets + sector concentration (30% max) + intraday refresh |
| **Volatility Targeting** | Scales position sizes so daily portfolio vol = 1% target |
| **Daily P&L Lock** | GAIN_LOCK at +1.5% (30% sizing), LOSS_HALT at -1.0% (stops new trades) |
| **Beta Neutralization** | Monitors portfolio beta, hedges with SPY when \|beta\| > 0.3 |
| **Transaction Cost Filter** | Rejects negative expected-value trades before submission |
| **Kill Switch** | Emergency halt: cancels all orders, closes all positions |
| **TWAP Execution** | Orders > $2,000 split into 5 time-weighted slices |
| **API Failure Breaker** | 5 failures in 5 min triggers kill switch |
| **Drawdown Sizing** | Dynamic position scaling based on cumulative daily drawdown |
| **Time-of-Day Multiplier** | Tighter sizing at market open/close, Friday risk reduction |

---

## Docker

```bash
docker compose up -d                              # velox + daily backup
docker attach velox-v12                           # live terminal dashboard (detach: Ctrl-P Ctrl-Q)
docker compose logs -f velox                      # follow logs
docker compose exec velox python velox.py status  # positions and trades
docker compose exec velox python velox.py kill    # emergency stop
```

The container health check runs `velox health`, which checks that the main loop's heartbeat is fresh. Configure everything in `.env` (see `.env.example`).

---

## Configuration

| Parameter | Default | Description |
|---|---|---|
| `ALPACA_LIVE` | `false` | Paper vs live trading |
| `MAX_POSITIONS` | `12` | Maximum concurrent positions |
| `MAX_POSITION_PCT` | `8%` | Maximum position size as % of portfolio |
| `SCAN_INTERVAL_SEC` | `120` | Seconds between strategy scans (adaptive) |
| `RISK_PER_TRADE_PCT` | `0.8%` | Max risk per trade |
| `VOL_TARGET_DAILY` | `1.0%` | Daily portfolio volatility target |
| `STRUCTURED_LOGGING` | `false` | Enable JSON structured logging |
| `WATCHDOG_ENABLED` | `false` | Enable position watchdog |
| `NEWS_SENTIMENT_ENABLED` | `true` | Enable Alpaca news sentiment filter |
| `FINBERT_ENABLED` | `true` | Enable local FinBERT sentiment scoring |
| `ML_GATING_ENABLED` | `true` | Enable ML confidence gating on signals |
| `LLM_SCORING_ENABLED` | `false` | Enable Claude Haiku signal scoring |
| `ADAPTIVE_EXITS_ENABLED` | `true` | Enable VIX-aware adaptive exits |
| `WALK_FORWARD_ENABLED` | `true` | Enable weekly walk-forward validation |
| `TAX_HARVESTING_ENABLED` | `true` | Enable Friday EOD tax-loss harvesting |
| `TELEGRAM_ENABLED` | `false` | Enable Telegram trade alerts |
| `ALLOW_SHORT` | `false` | Enable short selling |

---

## Backtesting and Reports

```bash
velox backtest                                  # all baselines on bundled sample data (data/samples)
velox backtest --strategy rsi --symbols AAPL,SPY
velox backtest --start 2023-01-01 --symbols NVDA   # fetch daily bars from yfinance
velox backtest --strategy velox                 # the production strategies' simulations

velox tearsheet --days 90                       # performance report from bot.db
```

The baselines (EMA crossover, RSI reversal, momentum, Bollinger mean reversion) trade daily bars long-only with next-open fills and exist as yardsticks: a Velox strategy that cannot beat them is not earning its allocation.

---

## Testing

```bash
# Run all tests (TESTING=1 skips the Alpaca-credential check)
TESTING=1 pytest tests/ -v

# With coverage
pytest tests/ -v --cov=. --cov-report=html

# Run specific modules
pytest tests/test_v12_exit_orchestrator.py -v
pytest tests/test_v10_oms.py -v
pytest tests/test_v10_events.py -v
pytest tests/test_v10_phase4.py -v
```

1,870+ tests across 88 test files covering all strategies, risk modules, OMS, exit orchestrator, event bus, circuit breaker, ML pipeline, and analytics.

---

## Version History

| Version | Date | Focus |
|---|---|---|
| V1 | 2025-01 | ORB + VWAP strategies, basic risk management |
| V2 | 2025-05 | Momentum strategy, WebSocket monitoring |
| V3 | 2025-09 | ML signal filter, short selling, dynamic allocation |
| V4 | 2026-03 | Sector rotation, pairs trading, MTF, news filter |
| V5 | 2026-03 | EMA scalping, shadow mode, advanced exits |
| V6 | 2026-03 | Complete rebuild: statistical mean reversion, vol targeting |
| V7 | 2026-03 | 5-strategy diversification, news sentiment, LLM scoring, adaptive exits |
| V8 | 2026-03 | Bug fixes, thread safety, dead code removal |
| V9 | 2026-03 | Engine decomposition, OMS skeleton |
| V10 | 2026-03 | Production-grade: tiered circuit breaker, VaR monitor, correlation limiter, event bus, structured logging, Prometheus metrics, Docker stack, Apple-style dashboard |
| V11 | 2026-03 | ML ensemble (50 features, 0.947 AUC), FinBERT sentiment, Bayesian Kelly sizing |
| V12 | 2026-04 | **Unified ExitOrchestrator, 18-stage signal pipeline, position recovery, corporate actions monitoring, tax-loss harvesting, intraday correlation refresh, profit maximizer, data feed monitoring, health alerts, 6-service Docker stack** |

| **V13** | **2026-10** | **Terminal-only: web dashboard, Prometheus/Grafana and JWT auth removed; `velox` CLI with a terminal kill switch; classic baselines ported from the Rust project; AlphaFlow and Trading Algorithms merged in (history preserved); relicensed MIT** |

---

## Lineage

Velox grew out of two earlier projects, both merged into this repository with their git history intact under [`legacy/`](legacy/):

- **AlphaFlow** (`legacy/alphaflow`): the original Python/FastAPI trading platform for Alpaca (strategy engine, backtester, risk manager, React UI). Velox is its direct successor, so the project is "Velox, formerly AlphaFlow".
- **Trading Algorithms** (`legacy/trading-algorithms`): a Rust workspace with SIMD indicators, a backtester and paper trading. Its classic strategies (MA crossover, RSI, momentum, Bollinger mean reversion) now live on as the `velox backtest` baselines in `backtesting/baselines.py`, and its sample market data ships in `data/samples/`.

Secrets, `node_modules` and logs were stripped from both histories before the import.

---

## Risk Warning

> **This is experimental software. Use at your own risk. Past performance is not indicative of future results.** Trading equities involves substantial risk of loss. This software is provided for educational and research purposes. The authors are not responsible for any financial losses incurred through the use of this software.

---

## License

Released under the [MIT License](LICENSE).

See also: [CONTRIBUTING](CONTRIBUTING.md) · [SECURITY](SECURITY.md) · [CHANGELOG](CHANGELOG.md) · [Code of Conduct](CODE_OF_CONDUCT.md)

# CLAUDE.md

Guidance for Claude Code when working in this repository.

# Velox (formerly AlphaFlow): terminal equity trading system

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env              # ALPACA_API_KEY / ALPACA_API_SECRET (paper keys)

python velox.py demo              # dashboard with synthetic data, no broker needed
python velox.py backtest          # classic baselines on data/samples (or --start YYYY-MM-DD for yfinance)
python velox.py run               # live bot + terminal dashboard (paper by default)
python velox.py status --watch    # heartbeat, positions, trades
python velox.py kill              # ask the running bot to close everything

TESTING=1 pytest tests/ -q --ignore=tests/test_stress_testing.py
TESTING=1 pytest tests/test_baselines.py -v          # single file
```

`TESTING=1` skips the Alpaca-credential check in `config/settings.py`; set it for every pytest run and for any script that imports `config` without real keys.

## Architecture

- `velox.py` is the only CLI. Subcommands live in `cmd_*` functions; `run`, `start` and `tearsheet` forward leading options to the script they wrap.
- `main.py` is the orchestrator: startup, position recovery, then the synchronous main loop (1 s tick, scans every `SCAN_INTERVAL_SEC`). The loop writes `heartbeat.json` every 30 s and consumes `models/kill_request.json` (written by `velox kill`).
- `engine/signal_processor.py` runs every signal through gates, risk limits, sizing and a bracket order. `engine/exit_orchestrator.py` owns all exit decisions (10-level priority cascade). `engine/scanner.py` runs the strategies in `strategies/`.
- `risk/` (circuit breaker, VaR, correlation limiter, vol targeting, P&L lock), `oms/` (order state machine, kill switch), `execution/` (bracket orders, TWAP), `ml/` (ensemble inference, FinBERT), `analytics/`, `backtesting/`, `data/`.
- State is SQLite only (`bot.db` via `database.py`). There is no web server, no PostgreSQL and no Prometheus. The interface is the Rich dashboard (`dashboard.py`) and the `velox` commands.
- Strategy allocations and all tunables are in `config/settings.py` (`STRATEGY_ALLOCATIONS`; ORB is demoted to 0.0 but its code is kept).
- `backtesting/baselines.py` holds long-only daily-bar baselines (EMA crossover, RSI, momentum, Bollinger). They are benchmarks for `velox backtest`, never traded live.
- `website/index.html` is the single-file project site (deployed to velox.braunf.com by `.github/workflows/pages.yml`).

## Conventions

- Fail open: wrap optional integrations in try/except and never let them crash the main loop. Safety paths (kill switch, circuit breaker, stops) must fail closed.
- New features behind config flags, with tests. Signals must go through `process_signals`.
- Telegram, the web dashboard and PostgreSQL were removed on purpose; do not reintroduce them.
- Do not commit `.env`, `bot.db`, `bot.log`, `audit.log` or `heartbeat.json` (all gitignored).
- `main` is protected: open a PR. CI runs the suite on Python 3.12 and 3.13, gitleaks and a Docker smoke test.
- History was rewritten on 2026-10-18 to remove leaked files; old clones must be re-cloned. The predecessor projects live in history (`archive/alphaflow-final`, `archive/trading-algorithms-final` tags).

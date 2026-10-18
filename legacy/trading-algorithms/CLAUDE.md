# Trading Algorithms — Rust System

```bash
cargo build --release
./target/release/trading strategies
./target/release/trading backtest --strategy ma_crossover --symbols AAPL --start 2023-01-01 --end 2024-01-01 --capital 100000 --data ./data
./target/release/trading paper --strategy rsi --symbols SPY,QQQ --capital 50000 --timeframe 5m

cargo test --workspace
cargo test -p trading-strategies    # single crate
cargo bench
cargo fmt && cargo clippy --workspace
```

**Architecture:** Multi-crate workspace: `trading-core` (types/traits), `trading-indicators` (SIMD), `trading-strategies`, `trading-risk`, `trading-data`, `trading-broker`, `trading-backtest`, `trading-monitor` (TUI), `trading-config`. Config in `config/default.toml`; Alpaca keys via env vars or config file.

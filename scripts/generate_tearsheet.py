#!/usr/bin/env python3
"""Performance tear sheet generator for Velox Trading Bot.

Reads trade history and daily snapshots from bot.db, computes comprehensive
performance metrics, and prints a Rich-formatted terminal report.

Usage:
    python3 scripts/generate_tearsheet.py              # Full history
    python3 scripts/generate_tearsheet.py --days 90    # Last 90 days
"""

import argparse
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Optional imports -- degrade gracefully
# ---------------------------------------------------------------------------
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text

    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TRADING_DAYS_PER_YEAR = 252
RISK_FREE_RATE = 0.045  # 4.5% annual
DB_PATH = Path(__file__).resolve().parent.parent / "bot.db"


# ============================================================================
# Data loading
# ============================================================================

def load_trades(db_path: str, days: int | None = None) -> list[dict]:
    """Load closed trades from the database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    query = "SELECT * FROM trades ORDER BY exit_time ASC"
    rows = conn.execute(query).fetchall()
    conn.close()

    trades = [dict(r) for r in rows]

    if days and trades:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        trades = [t for t in trades if (t.get("exit_time") or "") >= cutoff]

    return trades


def load_snapshots(db_path: str, days: int | None = None) -> list[dict]:
    """Load daily portfolio snapshots from the database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    query = "SELECT * FROM daily_snapshots ORDER BY date ASC"
    rows = conn.execute(query).fetchall()
    conn.close()

    snapshots = [dict(r) for r in rows]

    if days and snapshots:
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        snapshots = [s for s in snapshots if s["date"] >= cutoff]

    return snapshots


# ============================================================================
# Metric computations
# ============================================================================

def compute_daily_returns(snapshots: list[dict]) -> np.ndarray:
    """Extract daily return percentages from snapshots."""
    if len(snapshots) < 2:
        return np.array([])
    return np.array([s["day_pnl_pct"] for s in snapshots[1:] if s["day_pnl_pct"] is not None])


def sharpe_ratio(daily_returns: np.ndarray) -> float:
    if len(daily_returns) < 2:
        return 0.0
    daily_rf = RISK_FREE_RATE / TRADING_DAYS_PER_YEAR
    excess = daily_returns - daily_rf
    std = np.std(excess, ddof=1)
    if std == 0:
        return 0.0
    return float(np.mean(excess) / std * np.sqrt(TRADING_DAYS_PER_YEAR))


def sortino_ratio(daily_returns: np.ndarray) -> float:
    if len(daily_returns) < 2:
        return 0.0
    daily_rf = RISK_FREE_RATE / TRADING_DAYS_PER_YEAR
    excess = daily_returns - daily_rf
    downside = excess[excess < 0]
    if len(downside) == 0:
        return 99.9 if np.mean(excess) > 0 else 0.0
    ds_std = np.std(downside, ddof=1)
    if ds_std == 0:
        return 0.0
    return float(np.mean(excess) / ds_std * np.sqrt(TRADING_DAYS_PER_YEAR))


def calmar_ratio(ann_return: float, max_dd: float) -> float:
    if max_dd == 0:
        return 0.0
    return ann_return / abs(max_dd)


def max_drawdown_series(portfolio_values: list[float]) -> tuple[float, int, list[float]]:
    """Returns (max_dd_pct, duration_in_days, drawdown_series)."""
    if len(portfolio_values) < 2:
        return 0.0, 0, []

    arr = np.array(portfolio_values, dtype=float)
    running_max = np.maximum.accumulate(arr)
    drawdown = (arr - running_max) / running_max
    max_dd = float(np.min(drawdown))

    # Compute duration of worst drawdown
    duration = 0
    current_duration = 0
    max_duration = 0
    in_drawdown = False
    for dd in drawdown:
        if dd < 0:
            current_duration += 1
            if current_duration > max_duration:
                max_duration = current_duration
        else:
            current_duration = 0

    return max_dd, max_duration, drawdown.tolist()


def profit_factor(trades: list[dict]) -> float:
    gross_profit = sum(t["pnl"] for t in trades if (t.get("pnl") or 0) > 0)
    gross_loss = abs(sum(t["pnl"] for t in trades if (t.get("pnl") or 0) < 0))
    if gross_loss == 0:
        return 99.9 if gross_profit > 0 else 0.0
    return gross_profit / gross_loss


def win_rate(trades: list[dict]) -> float:
    if not trades:
        return 0.0
    winners = sum(1 for t in trades if (t.get("pnl") or 0) > 0)
    return winners / len(trades) * 100


def avg_hold_time(trades: list[dict]) -> timedelta:
    """Average holding time across trades."""
    durations = []
    for t in trades:
        entry = t.get("entry_time")
        exit_ = t.get("exit_time")
        if entry and exit_:
            try:
                # Parse ISO format (may have timezone info)
                e = datetime.fromisoformat(entry)
                x = datetime.fromisoformat(exit_)
                durations.append((x - e).total_seconds())
            except (ValueError, TypeError):
                continue
    if not durations:
        return timedelta(0)
    return timedelta(seconds=sum(durations) / len(durations))


def consecutive_streaks(trades: list[dict]) -> tuple[int, int]:
    """Returns (max_win_streak, max_loss_streak)."""
    if not trades:
        return 0, 0
    max_win = max_loss = 0
    cur_win = cur_loss = 0
    for t in trades:
        pnl = t.get("pnl") or 0
        if pnl > 0:
            cur_win += 1
            cur_loss = 0
        elif pnl < 0:
            cur_loss += 1
            cur_win = 0
        else:
            cur_win = cur_loss = 0
        max_win = max(max_win, cur_win)
        max_loss = max(max_loss, cur_loss)
    return max_win, max_loss


def compute_var_95(daily_returns: np.ndarray) -> float:
    """Historical VaR at 95% confidence (parametric)."""
    if len(daily_returns) < 5:
        return 0.0
    return float(np.percentile(daily_returns, 5))


def compute_monthly_returns(snapshots: list[dict]) -> dict[tuple[int, int], float]:
    """Compute monthly returns from snapshots. Key = (year, month)."""
    if len(snapshots) < 2:
        return {}

    monthly = {}
    # Group snapshots by year-month
    by_month: dict[tuple[int, int], list[dict]] = {}
    for s in snapshots:
        try:
            d = datetime.strptime(s["date"], "%Y-%m-%d")
        except (ValueError, TypeError):
            continue
        key = (d.year, d.month)
        by_month.setdefault(key, []).append(s)

    for key, month_snaps in by_month.items():
        month_snaps.sort(key=lambda s: s["date"])
        first_val = month_snaps[0]["portfolio_value"]
        last_val = month_snaps[-1]["portfolio_value"]
        if first_val and first_val > 0:
            monthly[key] = (last_val - first_val) / first_val * 100
        else:
            monthly[key] = 0.0

    return monthly


def compute_strategy_breakdown(trades: list[dict], daily_returns: np.ndarray) -> list[dict]:
    """Per-strategy performance breakdown."""
    by_strategy: dict[str, list[dict]] = {}
    for t in trades:
        strat = t.get("strategy", "Unknown")
        by_strategy.setdefault(strat, []).append(t)

    results = []
    for strat, strat_trades in by_strategy.items():
        pnls = [t.get("pnl") or 0 for t in strat_trades]
        winners = sum(1 for p in pnls if p > 0)
        total_pnl = sum(pnls)

        # Strategy-level Sharpe approximation from trade P&L percentages
        pnl_pcts = [t.get("pnl_pct") or 0 for t in strat_trades]
        strat_sharpe = 0.0
        if len(pnl_pcts) >= 2:
            arr = np.array(pnl_pcts)
            std = np.std(arr, ddof=1)
            if std > 0:
                strat_sharpe = float(np.mean(arr) / std * np.sqrt(TRADING_DAYS_PER_YEAR))

        results.append({
            "strategy": strat,
            "trades": len(strat_trades),
            "win_rate": winners / len(strat_trades) * 100 if strat_trades else 0,
            "avg_pnl": sum(pnls) / len(pnls) if pnls else 0,
            "sharpe": strat_sharpe,
            "total_pnl": total_pnl,
        })

    results.sort(key=lambda r: r["total_pnl"], reverse=True)
    return results


# ============================================================================
# Terminal output (Rich)
# ============================================================================

def _fmt_pct(val: float, decimals: int = 2) -> str:
    """Format percentage with sign."""
    sign = "+" if val > 0 else ""
    return f"{sign}{val:.{decimals}f}%"


def _fmt_dollar(val: float) -> str:
    """Format dollar amount with sign."""
    sign = "+" if val > 0 else ""
    return f"{sign}${val:,.2f}"


def _fmt_duration(td: timedelta) -> str:
    """Format timedelta as human-readable."""
    total_seconds = int(td.total_seconds())
    if total_seconds < 0:
        return "0m"
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts)


def print_terminal_report(
    trades: list[dict],
    snapshots: list[dict],
    daily_returns: np.ndarray,
    strategy_breakdown: list[dict],
    monthly_returns: dict,
    max_dd: float,
    dd_duration: int,
    days_filter: int | None,
):
    """Print the tear sheet to terminal using Rich."""
    if not HAS_RICH:
        print("[WARNING] Install 'rich' for formatted terminal output: pip install rich")
        print(f"Total trades: {len(trades)}")
        print(f"Snapshots: {len(snapshots)}")
        return

    console = Console()
    console.print()

    # Title
    title_text = "VELOX TRADING BOT -- PERFORMANCE TEAR SHEET"
    if days_filter:
        title_text += f"  (Last {days_filter} days)"
    console.print(Panel(f"[bold white]{title_text}[/]", border_style="cyan", expand=True))

    if not trades:
        console.print("[yellow]No trades found in the database.[/]")
        return

    # Dates
    start_date = snapshots[0]["date"] if snapshots else "N/A"
    end_date = snapshots[-1]["date"] if snapshots else "N/A"
    total_pnl = sum(t.get("pnl") or 0 for t in trades)

    # Portfolio values for return calc
    if snapshots:
        initial_val = snapshots[0]["portfolio_value"]
        final_val = snapshots[-1]["portfolio_value"]
        total_return = (final_val - initial_val) / initial_val * 100 if initial_val else 0
        n_days = len(snapshots)
        ann_factor = TRADING_DAYS_PER_YEAR / max(n_days, 1)
        ann_return = ((1 + total_return / 100) ** ann_factor - 1) * 100
    else:
        total_return = ann_return = 0.0

    sharpe = sharpe_ratio(daily_returns)
    sortino = sortino_ratio(daily_returns)
    calmar = calmar_ratio(ann_return / 100, max_dd)
    pf = profit_factor(trades)
    wr = win_rate(trades)
    avg_pnl = total_pnl / len(trades) if trades else 0
    hold = avg_hold_time(trades)

    # --- Section 1: Summary ---
    summary = Table(title="Summary Statistics", show_header=True, header_style="bold cyan",
                    border_style="dim", title_style="bold white")
    summary.add_column("Metric", style="white", width=28)
    summary.add_column("Value", justify="right", width=20)

    summary.add_row("Trading Period", f"{start_date}  --  {end_date}")
    summary.add_row("Total Return", _fmt_pct(total_return))
    summary.add_row("Annualized Return", _fmt_pct(ann_return))
    summary.add_row("Sharpe Ratio", f"{sharpe:.2f}")
    summary.add_row("Sortino Ratio", f"{sortino:.2f}")
    summary.add_row("Calmar Ratio", f"{calmar:.2f}")
    summary.add_row("Max Drawdown", f"{max_dd * 100:.2f}%  ({dd_duration}d)")
    summary.add_row("Win Rate", f"{wr:.1f}%")
    summary.add_row("Profit Factor", f"{pf:.2f}")
    summary.add_row("Total Trades", str(len(trades)))
    summary.add_row("Avg Trade P&L", _fmt_dollar(avg_pnl))
    summary.add_row("Avg Hold Time", _fmt_duration(hold))

    console.print(summary)
    console.print()

    # --- Section 2: Monthly Returns ---
    if monthly_returns:
        years = sorted(set(k[0] for k in monthly_returns.keys()))
        months_table = Table(title="Monthly Returns (%)", show_header=True,
                             header_style="bold cyan", border_style="dim",
                             title_style="bold white")
        months_table.add_column("Year", style="white", width=6)
        for m in range(1, 13):
            months_table.add_column(datetime(2000, m, 1).strftime("%b"), justify="right", width=7)
        months_table.add_column("YTD", justify="right", width=8, style="bold")

        for year in years:
            row = [str(year)]
            ytd = 0.0
            for m in range(1, 13):
                val = monthly_returns.get((year, m))
                if val is not None:
                    color = "green" if val >= 0 else "red"
                    row.append(f"[{color}]{val:+.1f}[/]")
                    ytd += val
                else:
                    row.append("[dim]--[/]")
            color = "green" if ytd >= 0 else "red"
            row.append(f"[{color}]{ytd:+.1f}[/]")
            months_table.add_row(*row)

        console.print(months_table)
        console.print()

    # --- Section 3: Strategy Breakdown ---
    if strategy_breakdown:
        strat_table = Table(title="Strategy Breakdown", show_header=True,
                            header_style="bold cyan", border_style="dim",
                            title_style="bold white")
        strat_table.add_column("Strategy", style="white", width=20)
        strat_table.add_column("Trades", justify="right", width=8)
        strat_table.add_column("Win Rate", justify="right", width=10)
        strat_table.add_column("Avg P&L", justify="right", width=12)
        strat_table.add_column("Sharpe", justify="right", width=8)
        strat_table.add_column("Total P&L", justify="right", width=14)

        for s in strategy_breakdown:
            pnl_color = "green" if s["total_pnl"] >= 0 else "red"
            strat_table.add_row(
                s["strategy"],
                str(s["trades"]),
                f"{s['win_rate']:.1f}%",
                _fmt_dollar(s["avg_pnl"]),
                f"{s['sharpe']:.2f}",
                f"[{pnl_color}]{_fmt_dollar(s['total_pnl'])}[/]",
            )

        console.print(strat_table)
        console.print()

    # --- Section 5: Risk Metrics ---
    var_95 = compute_var_95(daily_returns)
    vol = float(np.std(daily_returns, ddof=1)) if len(daily_returns) > 1 else 0.0
    best_day = float(np.max(daily_returns)) if len(daily_returns) > 0 else 0.0
    worst_day = float(np.min(daily_returns)) if len(daily_returns) > 0 else 0.0
    best_trade = max((t.get("pnl") or 0 for t in trades), default=0)
    worst_trade = min((t.get("pnl") or 0 for t in trades), default=0)
    win_streak, loss_streak = consecutive_streaks(trades)

    # Average exposure
    if snapshots:
        exposures = []
        for s in snapshots:
            pv = s.get("portfolio_value") or 0
            cash = s.get("cash") or 0
            if pv > 0:
                exposures.append((pv - cash) / pv * 100)
        avg_exposure = sum(exposures) / len(exposures) if exposures else 0
    else:
        avg_exposure = 0

    risk_table = Table(title="Risk Metrics", show_header=True, header_style="bold cyan",
                       border_style="dim", title_style="bold white")
    risk_table.add_column("Metric", style="white", width=28)
    risk_table.add_column("Value", justify="right", width=20)

    risk_table.add_row("Daily VaR (95%)", _fmt_pct(var_95 * 100))
    risk_table.add_row("Daily P&L Volatility", _fmt_pct(vol * 100))
    risk_table.add_row("Best Day", _fmt_pct(best_day * 100))
    risk_table.add_row("Worst Day", _fmt_pct(worst_day * 100))
    risk_table.add_row("Best Trade", _fmt_dollar(best_trade))
    risk_table.add_row("Worst Trade", _fmt_dollar(worst_trade))
    risk_table.add_row("Max Win Streak", f"{win_streak} trades")
    risk_table.add_row("Max Loss Streak", f"{loss_streak} trades")
    risk_table.add_row("Avg Exposure", f"{avg_exposure:.1f}%")

    console.print(risk_table)
    console.print()


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate Velox performance tear sheet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--days", type=int, default=None,
        help="Limit to last N days (default: full history)",
    )
    parser.add_argument(
        "--db", type=str, default=str(DB_PATH),
        help=f"Path to database (default: {DB_PATH})",
    )
    args = parser.parse_args()

    db_path = args.db
    if not Path(db_path).exists():
        print(f"ERROR: Database not found at {db_path}")
        sys.exit(1)

    # Load data
    trades = load_trades(db_path, args.days)
    snapshots = load_snapshots(db_path, args.days)

    if not trades and not snapshots:
        print("No data found in database. Run the trading bot first.")
        sys.exit(0)

    # Compute metrics
    daily_returns = compute_daily_returns(snapshots)
    portfolio_values = [s["portfolio_value"] for s in snapshots] if snapshots else []
    max_dd, dd_duration, _ = max_drawdown_series(portfolio_values)
    strategy_breakdown = compute_strategy_breakdown(trades, daily_returns)
    monthly_returns = compute_monthly_returns(snapshots)

    # Terminal output
    print_terminal_report(
        trades, snapshots, daily_returns, strategy_breakdown,
        monthly_returns, max_dd, dd_duration, args.days,
    )


if __name__ == "__main__":
    main()

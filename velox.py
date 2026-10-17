#!/usr/bin/env python3
"""Velox command line: run, monitor, control and benchmark the trading system.

    velox run [--live] [--diagnose]   Start the bot with the live terminal dashboard
    velox start | stop                Run the bot in the background / stop it gracefully
    velox status [--watch]            Heartbeat, open positions and recent trades
    velox health                      Exit 0 if the heartbeat is fresh (health checks)
    velox kill                        Ask a running bot to close everything (kill switch)
    velox backtest [...]              Backtest the classic baselines (or Velox's strategies)
    velox tearsheet [...]             Performance report from the trade database
    velox demo                        Render the dashboard with synthetic data
    velox strategies                  List strategies and their allocations
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sqlite3
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

PID_FILE = ROOT / ".bot.pid"
HEARTBEAT_FILE = ROOT / "heartbeat.json"
LOG_FILE = ROOT / "bot.log"
HEARTBEAT_STALE_SEC = 300


# ---------------------------------------------------------------------------
# Process helpers
# ---------------------------------------------------------------------------

def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _running_pid() -> int | None:
    try:
        pid = int(PID_FILE.read_text().strip())
    except (FileNotFoundError, ValueError):
        return None
    return pid if _pid_alive(pid) else None


def _ago(seconds: float) -> str:
    if seconds < 120:
        return f"{seconds:.0f}s ago"
    if seconds < 7200:
        return f"{seconds / 60:.0f}m ago"
    if seconds < 172800:
        return f"{seconds / 3600:.0f}h ago"
    return f"{seconds / 86400:.0f}d ago"


def _heartbeat() -> dict | None:
    try:
        data = json.loads(HEARTBEAT_FILE.read_text())
        data["age_sec"] = (datetime.now() - datetime.fromisoformat(data["timestamp"])).total_seconds()
        return data
    except (FileNotFoundError, ValueError, KeyError):
        return None


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_run(args: argparse.Namespace) -> int:
    import runpy

    sys.argv = ["main.py", *args.extra]
    runpy.run_path(str(ROOT / "main.py"), run_name="__main__")
    return 0


def cmd_start(args: argparse.Namespace) -> int:
    if _running_pid():
        print(f"Velox is already running (PID {_running_pid()}).")
        return 1
    backup = ROOT / "scripts" / "backup.sh"
    if backup.exists():
        subprocess.run(["bash", str(backup)], cwd=ROOT, check=False)
    with open(LOG_FILE, "ab") as log:
        proc = subprocess.Popen([sys.executable, str(ROOT / "main.py"), *args.extra],
                                cwd=ROOT, stdout=log, stderr=log, start_new_session=True)
    PID_FILE.write_text(str(proc.pid))
    print(f"Velox started in the background (PID {proc.pid}). Logs: {LOG_FILE.name}")
    return 0


def cmd_stop(args: argparse.Namespace) -> int:
    pid = _running_pid()
    if not pid:
        print("Velox is not running.")
        PID_FILE.unlink(missing_ok=True)
        return 0
    print(f"Stopping Velox (PID {pid})...")
    os.kill(pid, signal.SIGINT)  # main.py shuts down cleanly on SIGINT
    for _ in range(args.timeout):
        if not _pid_alive(pid):
            PID_FILE.unlink(missing_ok=True)
            print("Stopped gracefully.")
            return 0
        time.sleep(1)
    print(f"Still running after {args.timeout}s. Force-stop with: kill -9 {pid}")
    return 1


def _status_renderable():
    from rich.console import Group
    from rich.table import Table
    from rich.text import Text

    pid = _running_pid()
    hb = _heartbeat()
    head = Table.grid(padding=(0, 2))
    if pid:
        head.add_row("Process", f"[green]running[/green] (PID {pid})")
    else:
        head.add_row("Process", "[red]stopped[/red]")
    if hb:
        fresh = hb["age_sec"] < HEARTBEAT_STALE_SEC
        color = "green" if fresh else "red"
        head.add_row("Heartbeat", f"[{color}]{_ago(hb['age_sec'])}[/{color}]")
    else:
        head.add_row("Heartbeat", "[yellow]none[/yellow]")

    parts = [Text("VELOX STATUS", style="bold cyan"), head]
    try:
        import database

        positions = database.load_open_positions()
        pos = Table(title=f"Open positions ({len(positions)})", expand=False)
        for col in ("Symbol", "Strategy", "Side", "Entry", "Qty", "B&H"):
            pos.add_column(col)
        for p in positions:
            pos.add_row(p["symbol"], p["strategy"], p["side"], f"${p['entry_price']:.2f}",
                        str(p["qty"]), p.get("hold_type", ""))
        parts.append(pos)

        trades = database.get_recent_trades(days=1)[:8]
        tr = Table(title="Closed in the last 24h", expand=False)
        for col in ("Exit", "Symbol", "Strategy", "P&L", "Reason"):
            tr.add_column(col)
        for t in trades:
            pnl = t["pnl"] or 0.0
            tr.add_row(str(t["exit_time"])[11:16], t["symbol"], t["strategy"],
                       f"[{'green' if pnl >= 0 else 'red'}]{pnl:+,.2f}[/]", t.get("exit_reason") or "")
        parts.append(tr)
    except sqlite3.OperationalError:  # bot has never run here, so no tables yet
        parts.append(Text("No trade database yet (the bot has not run in this directory).", style="yellow"))
    return Group(*parts)


def cmd_status(args: argparse.Namespace) -> int:
    os.environ.setdefault("TESTING", "1")  # read-only view, no broker credentials needed
    from rich.console import Console
    from rich.live import Live

    console = Console()
    if not args.watch:
        console.print(_status_renderable())
        return 0
    with Live(_status_renderable(), console=console, refresh_per_second=1, screen=True) as live:
        try:
            while True:
                time.sleep(args.interval)
                live.update(_status_renderable())
        except KeyboardInterrupt:
            return 0


def cmd_health(args: argparse.Namespace) -> int:
    """Exit 0 if the bot's heartbeat is fresh, 1 otherwise (Docker/systemd health check)."""
    hb = _heartbeat()
    return 0 if hb and hb["age_sec"] < args.max_age else 1


def cmd_kill(args: argparse.Namespace) -> int:
    os.environ.setdefault("TESTING", "1")
    from oms.kill_switch import request_kill

    hb = _heartbeat()
    alive = _running_pid() or (hb and hb["age_sec"] < HEARTBEAT_STALE_SEC)  # Docker has no PID file
    if not alive and not args.force:
        print("No running Velox process found. Use --force to queue the request anyway.")
        return 1
    if not args.yes:
        if input("Close ALL positions and cancel ALL orders? Type 'kill' to confirm: ").strip() != "kill":
            print("Aborted.")
            return 1
    path = request_kill(args.reason)
    print(f"Kill request written to {path}. The bot acts on it within one loop iteration.")
    return 0


def cmd_backtest(args: argparse.Namespace) -> int:
    os.environ.setdefault("TESTING", "1")
    from rich.console import Console
    from rich.table import Table

    from backtesting import baselines as bl

    if args.strategy == "velox":
        from backtester import run_backtest
        run_backtest()
        return 0

    names = list(bl.BASELINES) if args.strategy == "all" else [args.strategy]
    unknown = [n for n in names if n not in bl.BASELINES]
    if unknown:
        print(f"Unknown strategy {unknown[0]!r}. Choose from: all, velox, {', '.join(bl.BASELINES)}")
        return 2

    table = Table(title=f"Baseline backtest ({'CSV ' + str(args.csv_dir) if not args.start else args.start + ' to ' + args.end})")
    for col in ("Strategy", "Symbol", "Return", "Sharpe", "Win", "PF", "Max DD", "Trades", "B&H"):
        table.add_column(col, justify="right" if col not in ("Strategy", "Symbol") else "left")

    for symbol in [s.strip().upper() for s in args.symbols.split(",")]:
        try:
            bars = (bl.fetch_daily(symbol, args.start, args.end) if args.start
                    else bl.load_symbol(symbol, args.csv_dir))
        except (FileNotFoundError, ValueError) as e:
            Console().print(f"[red]{symbol}: {e}[/red]")
            continue
        for name in names:
            r = bl.run_baseline(name, symbol, bars, initial_capital=args.capital)
            table.add_row(name, symbol, f"{r.total_return:+.1%}",
                          f"{r.sharpe_ratio:.2f}", f"{r.win_rate:.0%}", f"{r.profit_factor:.2f}",
                          f"{r.max_drawdown:.1%}", str(r.total_trades), f"{bl.buy_and_hold(bars):+.1%}")
    Console().print(table)
    return 0


def cmd_tearsheet(args: argparse.Namespace) -> int:
    from scripts import generate_tearsheet

    sys.argv = ["tearsheet", *args.extra]
    generate_tearsheet.main()
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    from scripts import demo_dashboard

    demo_dashboard.main()
    return 0


def cmd_strategies(args: argparse.Namespace) -> int:
    os.environ.setdefault("TESTING", "1")
    from rich.console import Console
    from rich.table import Table

    import config
    from backtesting import baselines as bl

    live = Table(title="Production strategies")
    live.add_column("Name")
    live.add_column("Allocation", justify="right")
    for name, weight in sorted(config.STRATEGY_ALLOCATIONS.items(), key=lambda kv: -kv[1]):
        live.add_row(name, f"{weight:.0%}" if weight else "[dim]disabled[/dim]")
    base = Table(title="Backtest baselines (velox backtest --strategy NAME)")
    base.add_column("Name")
    base.add_column("Description")
    for b in bl.BASELINES.values():
        base.add_row(b.name, b.description)
    console = Console()
    console.print(live)
    console.print(base)
    return 0


# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="velox", description="Velox: terminal algorithmic trading system")
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name, func, help_, extra=False):
        p = sub.add_parser(name, help=help_)
        p.set_defaults(func=func)
        if extra:
            p.add_argument("extra", nargs=argparse.REMAINDER, help="arguments passed through")
        return p

    add("run", cmd_run, "run the bot in this terminal (live dashboard)", extra=True)
    add("start", cmd_start, "run the bot in the background", extra=True)
    p = add("stop", cmd_stop, "stop the background bot gracefully")
    p.add_argument("--timeout", type=int, default=30)

    p = add("status", cmd_status, "show heartbeat, positions and recent trades")
    p.add_argument("--watch", action="store_true", help="full-screen live refresh")
    p.add_argument("--interval", type=float, default=5.0)

    p = add("health", cmd_health, "exit 0 if the heartbeat is fresh (for Docker/systemd)")
    p.add_argument("--max-age", type=float, default=HEARTBEAT_STALE_SEC)

    p = add("kill", cmd_kill, "emergency: close all positions and cancel all orders")
    p.add_argument("--reason", default="manual (velox kill)")
    p.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    p.add_argument("--force", action="store_true", help="queue the request even if no bot is running")

    p = add("backtest", cmd_backtest, "backtest baseline strategies, or 'velox' for the production engine")
    p.add_argument("--strategy", default="all", help="all | velox | ma_crossover | rsi | momentum | mean_reversion")
    p.add_argument("--symbols", default="AAPL,MSFT,SPY")
    p.add_argument("--csv-dir", default=str(ROOT / "data" / "samples"),
                   help="directory of <symbol>_daily.csv files (default: data/samples)")
    p.add_argument("--start", help="fetch daily bars from yfinance instead of CSV (YYYY-MM-DD)")
    p.add_argument("--end", default=datetime.now().strftime("%Y-%m-%d"))
    p.add_argument("--capital", type=float, default=100_000.0)

    add("tearsheet", cmd_tearsheet, "performance report from the trade database", extra=True)
    add("demo", cmd_demo, "render the dashboard with synthetic data")
    add("strategies", cmd_strategies, "list strategies and allocations")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args, unknown = parser.parse_known_args(argv)
    if unknown:
        if not hasattr(args, "extra"):
            parser.error(f"unrecognized arguments: {' '.join(unknown)}")
        args.extra = [*unknown, *args.extra]  # pass-through commands forward leading options
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())

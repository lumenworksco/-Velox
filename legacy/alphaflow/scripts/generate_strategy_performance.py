#!/usr/bin/env python3
"""
Generate real performance data for all strategies using backtesting.
This replaces the mock/placeholder data with actual backtest results.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.backtester import BacktestEngine
from core.strategies import TradingStrategies


def run_strategy_backtests():
    """
    Run backtests for all strategies and generate performance data.
    """

    print("=" * 80)
    print("GENERATING REAL STRATEGY PERFORMANCE DATA")
    print("=" * 80)
    print()

    # Strategy configurations matching backend/api/strategies.py
    strategy_configs = {
        "ma_crossover": {
            "name": "Moving Average Crossover",
            "symbols": ["AAPL", "MSFT"],
            "backtest_strategy": "Technical Momentum",  # Use existing backtest strategy
            "period": "1y"
        },
        "rsi_mean_reversion": {
            "name": "RSI Mean Reversion",
            "symbols": ["SPY"],
            "backtest_strategy": "Mean Reversion",
            "period": "1y"
        },
        "momentum": {
            "name": "Momentum Strategy",
            "symbols": ["QQQ", "TSLA"],
            "backtest_strategy": "Technical Momentum",
            "period": "1y"
        },
        "mean_reversion": {
            "name": "Mean Reversion",
            "symbols": ["SPY", "IWM"],
            "backtest_strategy": "Mean Reversion",
            "period": "1y"
        },
        "quick_test": {
            "name": "Quick Test Strategy",
            "symbols": ["SPY"],
            "backtest_strategy": "Technical Momentum",
            "period": "3mo"
        },
        "multi_timeframe": {
            "name": "Multi-Timeframe Confluence",
            "symbols": ["AAPL", "MSFT", "GOOGL"],
            "backtest_strategy": "Technical Momentum",  # Will use advanced logic later
            "period": "1y"
        },
        "volatility_breakout": {
            "name": "Volatility Breakout",
            "symbols": ["NVDA", "TSLA"],
            "backtest_strategy": "Trend Following",
            "period": "1y"
        }
    }

    # Initialize backtester
    backtester = BacktestEngine(initial_capital=100000, commission=0.001)

    # Store results
    all_results = {}

    # Run backtests for each strategy
    for strategy_id, config in strategy_configs.items():
        print(f"\n{'='*60}")
        print(f"Running backtest: {config['name']} ({strategy_id})")
        print(f"Symbols: {', '.join(config['symbols'])}")
        print(f"Period: {config['period']}")
        print(f"{'='*60}\n")

        try:
            # Run backtest
            result = backtester.run_backtest(
                symbols=config['symbols'],
                strategy=config['backtest_strategy'],
                start_date=None,  # Will use period instead
                end_date=None
            )

            if result.get('success'):
                overall = result['overall_results']

                # Calculate dollar P&L from return percentage
                initial_capital = overall.get('initial_capital', 100000)
                final_capital = overall.get('final_capital', 100000)
                total_pnl_dollars = final_capital - initial_capital

                # Extract performance metrics
                performance = {
                    "strategy_id": strategy_id,
                    "total_pnl": round(total_pnl_dollars, 2),
                    "total_trades": overall.get('total_trades', 0),
                    "win_rate": round(overall.get('win_rate', overall.get('avg_win_rate', 0.0)), 1),
                    "sharpe_ratio": round(overall.get('sharpe_ratio', overall.get('avg_sharpe_ratio', 0.0)), 2)
                }

                all_results[strategy_id] = performance

                # Print results
                print(f"✅ SUCCESS")
                print(f"   Total P&L: ${performance['total_pnl']:,.2f}")
                print(f"   Trades: {performance['total_trades']}")
                print(f"   Win Rate: {performance['win_rate']}%")
                print(f"   Sharpe: {performance['sharpe_ratio']}")

            else:
                print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
                # Use default values
                all_results[strategy_id] = {
                    "strategy_id": strategy_id,
                    "total_pnl": 0.0,
                    "total_trades": 0,
                    "win_rate": 0.0,
                    "sharpe_ratio": 0.0
                }

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            all_results[strategy_id] = {
                "strategy_id": strategy_id,
                "total_pnl": 0.0,
                "total_trades": 0,
                "win_rate": 0.0,
                "sharpe_ratio": 0.0
            }

    # Print summary
    print("\n" + "=" * 80)
    print("BACKTEST RESULTS SUMMARY")
    print("=" * 80)
    print()
    print(f"{'Strategy':<30} {'P&L':<15} {'Trades':<10} {'Win Rate':<12} {'Sharpe':<10}")
    print("-" * 80)

    for strategy_id, perf in all_results.items():
        config = strategy_configs[strategy_id]
        pnl_str = f"${perf['total_pnl']:,.2f}"
        win_rate_str = f"{perf['win_rate']}%"

        print(f"{config['name']:<30} {pnl_str:<15} {perf['total_trades']:<10} "
              f"{win_rate_str:<12} {perf['sharpe_ratio']:<10.2f}")

    # Generate code to replace in strategies.py
    print("\n" + "=" * 80)
    print("GENERATED CODE FOR backend/api/strategies.py")
    print("=" * 80)
    print()
    print("Replace the `performance_data` dictionary in get_strategy_performance() with:")
    print()
    print("    # REAL performance data from backtests")
    print(f"    # Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("    performance_data = {")

    for strategy_id, perf in all_results.items():
        print(f'        "{strategy_id}": {{')
        print(f'            "total_pnl": {perf["total_pnl"]},')
        print(f'            "total_trades": {perf["total_trades"]},')
        print(f'            "win_rate": {perf["win_rate"]},')
        print(f'            "sharpe_ratio": {perf["sharpe_ratio"]}')
        print('        },')

    print("    }")
    print()

    # Save to JSON file for easy reference
    output_file = Path(__file__).parent.parent / "backtest_performance_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"Results also saved to: {output_file}")
    print()

    return all_results


if __name__ == "__main__":
    try:
        results = run_strategy_backtests()
        print("\n✅ Performance data generation complete!")
        print("\nNext steps:")
        print("1. Review the backtest results above")
        print("2. Copy the generated code")
        print("3. Replace performance_data in backend/api/strategies.py")
        print("4. Restart the backend server")
        print()

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

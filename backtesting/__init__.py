"""Backtesting utilities: Monte Carlo robustness testing and classic baselines.

- MonteCarloTester: trade shuffling, skipping and parameter perturbation
- baselines: classic strategies to benchmark against (see ``velox backtest``)
"""

from backtesting.monte_carlo import MonteCarloTester, MonteCarloResult

__all__ = ["MonteCarloTester", "MonteCarloResult"]
